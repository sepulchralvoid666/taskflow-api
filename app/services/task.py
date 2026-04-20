import math

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User, UserRole
from app.schemas.task import TaskCreate, TaskListResponse, TaskRead, TaskUpdate


class TaskNotFoundError(Exception):
    """Raised when a task doesn't exist."""


class TaskPermissionError(Exception):
    """Raised when a user lacks permission for an action."""


def _apply_filters(
    stmt: Select,
    status: str | None = None,
    priority: str | None = None,
    search: str | None = None,
    owner_id: int | None = None,
) -> Select:
    """Apply optional filters to a task query."""
    if owner_id is not None:
        stmt = stmt.where(Task.owner_id == owner_id)
    if status:
        stmt = stmt.where(Task.status == TaskStatus(status))
    if priority:
        stmt = stmt.where(Task.priority == TaskPriority(priority))
    if search:
        stmt = stmt.where(Task.title.ilike(f"%{search}%"))
    return stmt


async def list_tasks(
    db: AsyncSession,
    user: User,
    page: int = 1,
    size: int = 20,
    status: str | None = None,
    priority: str | None = None,
    search: str | None = None,
) -> TaskListResponse:
    """List tasks with pagination and filtering. Non-admins see only their own."""
    base = select(Task).options(selectinload(Task.owner))
    owner_filter = None if user.role == UserRole.ADMIN else user.id
    base = _apply_filters(base, status=status, priority=priority, search=search, owner_id=owner_filter)

    # Count total
    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    # Paginate
    stmt = base.order_by(Task.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return TaskListResponse(
        items=[TaskRead.model_validate(t) for t in tasks],
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total else 1,
    )


async def get_task(db: AsyncSession, user: User, task_id: int) -> Task:
    """Get a single task by ID. Raises if not found or no permission."""
    result = await db.execute(select(Task).options(selectinload(Task.owner)).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundError(f"Task {task_id} not found")

    if user.role != UserRole.ADMIN and task.owner_id != user.id:
        raise TaskPermissionError("Not authorized to view this task")

    return task


async def create_task(db: AsyncSession, user: User, data: TaskCreate) -> Task:
    """Create a new task owned by the current user."""
    task = Task(
        title=data.title,
        description=data.description,
        priority=TaskPriority(data.priority),
        status=TaskStatus.TODO,
        owner_id=user.id,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def update_task(db: AsyncSession, user: User, task_id: int, data: TaskUpdate) -> Task:
    """Update a task. Only the owner (or admin) can update."""
    task = await get_task(db, user, task_id)

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.status is not None:
        task.status = TaskStatus(data.status)
    if data.priority is not None:
        task.priority = TaskPriority(data.priority)

    await db.flush()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, user: User, task_id: int) -> None:
    """Delete a task. Only the owner (or admin) can delete."""
    task = await get_task(db, user, task_id)
    await db.delete(task)
    await db.flush()
