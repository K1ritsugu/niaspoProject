from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import OrderStatus
from app.schemas.schemas import OrderStatusCreate

async def create_order_status(db: AsyncSession, status: OrderStatusCreate):
    db_status = OrderStatus(**status.dict())
    db.add(db_status)
    await db.commit()
    await db.refresh(db_status)
    return db_status

async def get_order_status(db: AsyncSession, status_id: int):
    result = await db.execute(select(OrderStatus).where(OrderStatus.id == status_id))
    return result.scalars().first()

async def get_order_statuses(db: AsyncSession, order_id: int, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(OrderStatus).where(OrderStatus.order_id == order_id).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def update_order_status(db: AsyncSession, status_id: int, new_status: str):
    status = await get_order_status(db, status_id)
    if status:
        status.status = new_status
        await db.commit()
        await db.refresh(status)
    return status