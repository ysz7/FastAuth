import pytest


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/auth/register", json={
        "email": "new@test.com",
        "username": "newuser",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@test.com"
    assert data["username"] == "newuser"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate(client, registered_user):
    response = await client.post("/auth/register", json={
        "email": registered_user["email"],
        "username": "otherusername",
        "password": "password123",
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client, registered_user):
    response = await client.post("/auth/login", json=registered_user)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, registered_user):
    response = await client.post("/auth/login", json={
        "email": registered_user["email"],
        "password": "wrongpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me(client, auth_tokens):
    response = await client.get("/auth/me", headers={
        "Authorization": f"Bearer {auth_tokens['access_token']}"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "user@test.com"


@pytest.mark.asyncio
async def test_me_without_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh(client, auth_tokens):
    response = await client.post("/auth/refresh", json={
        "refresh_token": auth_tokens["refresh_token"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != auth_tokens["refresh_token"]


@pytest.mark.asyncio
async def test_refresh_invalid_token(client):
    response = await client.post("/auth/refresh", json={
        "refresh_token": "invalidtoken"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client, auth_tokens):
    response = await client.post("/auth/logout", json={
        "refresh_token": auth_tokens["refresh_token"]
    }, headers={
        "Authorization": f"Bearer {auth_tokens['access_token']}"
    })
    assert response.status_code == 200

    me_response = await client.get("/auth/me", headers={
        "Authorization": f"Bearer {auth_tokens['access_token']}"
    })
    assert me_response.status_code == 401
