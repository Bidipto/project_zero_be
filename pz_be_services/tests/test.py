import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncicko
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/v1/health")
    assert response.status_code == 200
    assert "status" in response.json()

@pytest.mark.asyncio
async def test_user_register_and_login():
    # Register
    user_data = {
        "username": "testuser1",
        "email": "testuser1@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        reg_response = await ac.post("/v1/user/register", json=user_data)
    assert reg_response.status_code == 201
    reg_json = reg_response.json()
    assert reg_json["username"] == user_data["username"]
    assert reg_json["email"] == user_data["email"]

    # Login
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login_response = await ac.post("/v1/user/login", json=login_data)
    assert login_response.status_code == 202
    login_json = login_response.json()
    assert login_json["username"] == user_data["username"]
    assert "access_token" in login_json

@pytest.mark.asyncio
async def test_get_usernames():
   # after user register
    user_data = {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "full_name": "Test User2",
        "password": "testpassword456"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/v1/user/register", json=user_data)
        login_response = await ac.post("/v1/user/login", json={"username": user_data["username"], "password": user_data["password"]})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        usernames_response = await ac.get("/v1/user/usernames", headers=headers)
    assert usernames_response.status_code == 200
    assert "usernames" in usernames_response.json()

