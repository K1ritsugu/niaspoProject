from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.schemas.schemas import OrderStatusCreate, OrderStatusOut
from app.utils import crud

router = APIRouter()

@router.post("/status/", response_model=OrderStatusOut)
async def add_order_status(status: OrderStatusCreate, db: AsyncSession = Depends(get_db)):
    created_status = await crud.create_order_status(db, status)
    return created_status

@router.get("/status/{status_id}", response_model=OrderStatusOut)
async def read_order_status(status_id: int, db: AsyncSession = Depends(get_db)):
    status = await crud.get_order_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status

@router.get("/orders/{order_id}/status/", response_model=list[OrderStatusOut])
async def read_order_statuses(order_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    statuses = await crud.get_order_statuses(db, order_id, skip, limit)
    return statuses

@router.put("/status/{status_id}/", response_model=OrderStatusOut)
async def update_order_status(status_id: int, new_status: str, db: AsyncSession = Depends(get_db)):
    updated_status = await crud.update_order_status(db, status_id, new_status)
    if not updated_status:
        raise HTTPException(status_code=404, detail="Status not found")
    return updated_status