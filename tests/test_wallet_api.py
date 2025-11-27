import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import uuid

from app.main import app
from app.models import Base, Wallet
from app.db import get_db

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/test_db"  # Use a test DB

engine = create_async_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_wallet_operations(setup_db):
    wallet_id = uuid.uuid4()

    async with TestingSessionLocal() as session:
        wallet = Wallet(id=wallet_id, balance=0)
        session.add(wallet)
        await session.commit()

    response = client.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "DEPOSIT", "amount": 1000})
    assert response.status_code == 200
    assert response.json()["new_balance"] == 1000

    response = client.get(f"/api/v1/wallets/{wallet_id}")
    assert response.status_code == 200
    assert response.json()["balance"] == 1000

    response = client.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "WITHDRAW", "amount": 500})
    assert response.status_code == 200
    assert response.json()["new_balance"] == 500

    response = client.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "WITHDRAW", "amount": 1000})
    assert response.status_code == 400
    assert "Insufficient funds" in response.json()["detail"]

    response = client.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "INVALID", "amount": 100})
    assert response.status_code == 400