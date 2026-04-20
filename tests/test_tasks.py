import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, auth_headers):
    """Authenticated user can create a task."""
    response = await client.post("/api/v1/tasks", json={
        "title": "Write tests",
        "description": "Add pytest coverage",
        "priority": "high",
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Write tests"
    assert data["status"] == "todo"
    assert data["priority"] == "high"


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient, auth_headers):
    """User can list their tasks."""
    # Create a task first
    await client.post("/api/v1/tasks", json={"title": "Task 1"}, headers=auth_headers)

    response = await client.get("/api/v1/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_single_task(client: AsyncClient, auth_headers):
    """User can get a specific task by ID."""
    create = await client.post("/api/v1/tasks", json={"title": "Specific task"}, headers=auth_headers)
    task_id = create.json()["id"]

    response = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Specific task"


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, auth_headers):
    """User can update their task."""
    create = await client.post("/api/v1/tasks", json={"title": "Old title"}, headers=auth_headers)
    task_id = create.json()["id"]

    response = await client.put(f"/api/v1/tasks/{task_id}", json={
        "title": "New title",
        "status": "in_progress",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, auth_headers):
    """User can delete their task."""
    create = await client.post("/api/v1/tasks", json={"title": "Delete me"}, headers=auth_headers)
    task_id = create.json()["id"]

    response = await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204

    # Confirm it's gone
    get = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get.status_code == 404


@pytest.mark.asyncio
async def test_tasks_unauthenticated(client: AsyncClient):
    """Unauthenticated requests to tasks return 403."""
    response = await client.get("/api/v1/tasks")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_task_not_found(client: AsyncClient, auth_headers):
    """GET a nonexistent task returns 404."""
    response = await client.get("/api/v1/tasks/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_filter_tasks_by_status(client: AsyncClient, auth_headers):
    """Tasks can be filtered by status."""
    await client.post("/api/v1/tasks", json={"title": "Todo task", "priority": "low"}, headers=auth_headers)
    create = await client.post("/api/v1/tasks", json={"title": "Done task"}, headers=auth_headers)
    task_id = create.json()["id"]
    await client.put(f"/api/v1/tasks/{task_id}", json={"status": "done"}, headers=auth_headers)

    response = await client.get("/api/v1/tasks?status=done", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert all(t["status"] == "done" for t in data["items"])
