from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID, uuid4
from pydantic import BaseModel
from typing import Literal

from .db import get_db
from .models import Wallet

app = FastAPI(title="Wallet API", version="1.0")


class OperationRequest(BaseModel):
    operation_type: Literal["DEPOSIT", "WITHDRAW"]
    amount: int

    model_config = {"extra": "forbid"}


class WalletResponse(BaseModel):
    wallet_id: UUID
    balance: int


# Создание нового кошелька
@app.post("/api/v1/wallets", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(db: AsyncSession = Depends(get_db)):
    new_wallet = Wallet(balance=0)
    db.add(new_wallet)
    await db.commit()
    await db.refresh(new_wallet)
    return WalletResponse(wallet_id=new_wallet.id, balance=new_wallet.balance)


# Получение баланса
@app.get("/api/v1/wallets/{wallet_id}", response_model=WalletResponse)
async def get_wallet(wallet_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return WalletResponse(wallet_id=wallet.id, balance=wallet.balance)


# Операция пополнения/списания
@app.post("/api/v1/wallets/{wallet_id}/operation")
async def wallet_operation(
    wallet_id: UUID,
    op: OperationRequest,
    db: AsyncSession = Depends(get_db)
):
    # Блокируем строку на время транзакции — защита от гонки
    stmt = select(Wallet).where(Wallet.id == wallet_id).with_for_update()
    result = await db.execute(stmt)
    wallet = result.scalar_one_or_none()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if op.operation_type == "DEPOSIT":
        wallet.balance += op.amount
    else:  # WITHDRAW
        if wallet.balance < op.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        wallet.balance -= op.amount

    await db.commit()
    return {"status": "success", "new_balance": wallet.balance}