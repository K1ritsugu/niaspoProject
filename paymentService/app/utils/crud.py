import datetime 
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.models import Transaction, Order, Dish
from app.schemas.schemas import TransactionCreate, OrderCreate
from typing import List, Optional

async def create_transaction(db: AsyncSession, transaction: TransactionCreate):
    db_transaction = Transaction(
        user_id=transaction.user_id,
        amount=transaction.amount,
        payment_method=transaction.payment_method
    )
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction

async def get_transaction(db: AsyncSession, current_user: dict, transaction_id: int) -> Optional[Transaction]:
    result = await db.execute(select(Transaction).where(and_(Transaction.id == transaction_id, Transaction.user_id == current_user.get("id"))))
    return result.scalars().first()

async def get_transaction_inner(db: AsyncSession, transaction_id: int) -> Optional[Transaction]:
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    return result.scalars().first()

async def get_transactions(db: AsyncSession, current_user: dict, skip: int = 0, limit: int = 10) -> List[Transaction]:
    result = await db.execute(select(Transaction).where(Transaction.user_id == current_user.get("id")).offset(skip).limit(limit))
    return result.scalars().all()

async def update_transaction_status(db: AsyncSession, transaction_id: int, status: str) -> Optional[Transaction]:
    transaction = await get_transaction_inner(db, transaction_id)
    if transaction:
        transaction.status = status
        await db.commit()
        await db.refresh(transaction)
    return transaction

async def create_order(db: AsyncSession, order: OrderCreate, current_user: dict):
    try:
        transaction = await get_transaction_inner(db, order.transaction_id)
        if not transaction or transaction.user_id != current_user.get("id"):
            raise HTTPException(status_code=400, detail=f"Transaction with id '{order.transaction_id}' doesn't exist or doesn't belong to the current user.")

        for item in order.items:
            dish_exists = await db.execute(select(Dish).where(Dish.id == item.dish_id))
            if not dish_exists.scalars().first():
                raise HTTPException(status_code=400, detail=f"Dish with id '{item.dish_id}' doesn't exist.")

        db_order = Order(
            user_id=order.user_id,
            items=[item.model_dump() for item in order.items],
            transaction_id=order.transaction_id,
            payment_method=order.payment_method
        )
        db.add(db_order)
        await db.commit()
        await db.refresh(db_order)
        return db_order
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f"Transaction with id '{order.transaction_id}' doesn't exist.")

async def get_order(db: AsyncSession, order_id: int) -> Optional[Order]:
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalars().first()

async def get_orders(db: AsyncSession, current_user: dict, skip: int = 0, limit: int = 10) -> List[Order]:
    result = await db.execute(select(Order).where(Order.user_id == current_user.get("id")).offset(skip).limit(limit))
    return result.scalars().all()

async def update_order_status(db: AsyncSession, order_id: int, status: str) -> Optional[Order]:
    order = await get_order(db, order_id)
    if order:
        order.status = status
        if status == "completed":
            order.closed_at = datetime.now()
        await db.commit()
        await db.refresh(order)
    return order