import pytest
from httpx import AsyncClient

from app.models.user import UserRole


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """New user can register successfully."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "username": "newuser",
        "password": "securepassword123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert data["role"] == UserRole.USER.value


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """Cannot register with an already-taken email."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "another",
        "password": "securepassword123",
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user):
    """Cannot register with an already-taken username."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "another@example.com",
        "username": "testuser",
        "password": "securepassword123",
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """User can log in with correct credentials."""
    response = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "testpassword123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Login fails with wrong password."""
    response = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user):
    """Refresh token exchange works."""
    login = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "testpassword123",
    })
    refresh_token = login.json()["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers):
    """Authenticated user can fetch their own profile."""
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """Unauthenticated request to /me returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 403  # No Bearer token → 403 from HTTPBearer
