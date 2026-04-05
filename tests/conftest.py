import pytest
import pytest_asyncio
import fakeredis.aioredis
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.core.redis as redis_module
from app.core.database import Base, get_db
from app.core.limiter import limiter
from app.main import app

limiter.enabled = False

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    redis_module.redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncSession:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def registered_user(client):
    await client.post("/auth/register", json={
        "email": "user@test.com",
        "username": "testuser",
        "password": "password123",
    })
    return {"email": "user@test.com", "password": "password123"}


@pytest_asyncio.fixture
async def auth_tokens(client, registered_user):
    response = await client.post("/auth/login", json=registered_user)
    return response.json()
