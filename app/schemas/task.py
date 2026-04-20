from datetime import datetime

from pydantic import BaseModel, Field


# --- Task schemas ---

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: str = Field(default="medium", pattern=r"^(low|medium|high)$")


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: str | None = Field(default=None, pattern=r"^(todo|in_progress|done)$")
    priority: str | None = Field(default=None, pattern=r"^(low|medium|high)$")


class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    priority: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    items: list[TaskRead]
    total: int
    page: int
    size: int
    pages: int
