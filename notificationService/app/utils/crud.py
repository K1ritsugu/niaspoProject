from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.models import OrderStatus, Order
from app.schemas.schemas import OrderStatusCreate


async def create_order_status(db: AsyncSession, status: OrderStatusCreate):

    result = await db.execute(select(Order).where(Order.id == status.order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db_status = OrderStatus(
        order_id=status.order_id,
        status=status.status
    )
    db.add(db_status)
    await db.commit()
    await db.refresh(db_status)
    return db_status

async def get_order_status(db: AsyncSession, status_id: int):
    result = await db.execute(select(OrderStatus).where(OrderStatus.id == status_id))
    return result.scalars().first()

async def get_order_statuses(db: AsyncSession, order_id: int, current_user: dict):
    user_id = current_user.get("id")
    result = await db.execute(
        select(OrderStatus).join(Order, OrderStatus.order_id == Order.id).where(OrderStatus.order_id == order_id, Order.user_id == user_id)
    )
    return result.scalars().all()

async def update_order_status(db: AsyncSession, status_id: int, new_status: str):
    status = await get_order_status(db, status_id)
    if status:
        status.status = new_status
        await db.commit()
        await db.refresh(status)
    return status