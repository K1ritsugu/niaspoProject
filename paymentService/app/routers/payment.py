from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_admin_user
from app.schemas.schemas import TransactionCreate, TransactionOut, OrderCreate, OrderOut
from app.utils import crud
from asyncio import sleep
from app.dependencies import get_user

router = APIRouter()

@router.post("/pay/", response_model=TransactionOut)
async def process_payment(transaction: TransactionCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    # Мокаем операцию оплаты с задержкой 1 секунда
    try:
        await get_user(user_id=transaction.user_id, db=db)

    except HTTPException as e:
        raise e
    await sleep(1)
    created_transaction = await crud.create_transaction(db, transaction)
    # Обновляем статус транзакции
    await crud.update_transaction_status(db, created_transaction.id, "completed")
    return created_transaction

@router.get("/pay/{transaction_id}", response_model=TransactionOut)
async def read_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    transaction = await crud.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.post("/orders/", response_model=OrderOut)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    try:
        await get_user(user_id=order.user_id, db=db)

    except HTTPException as e:
        raise e
        
    created_order = await crud.create_order(db, order)
    return created_order

@router.get("/orders/{order_id}", response_model=OrderOut)
async def read_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/orders/", response_model=list[OrderOut])
async def read_orders(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    orders = await crud.get_orders(db, skip, limit)
    return orders

@router.put("/orders/{order_id}/status/", response_model=OrderOut)
async def update_order_status(order_id: int, status: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_admin_user)):
    updated_order = await crud.update_order_status(db, order_id, status)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order