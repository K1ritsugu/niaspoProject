from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_admin_user, get_current_user
from app.schemas.schemas import OrderStatusCreate, OrderStatusOut, OrderStatusEnum
from app.utils import crud

router = APIRouter()

@router.post("/status/", response_model=OrderStatusOut)
async def add_order_status(status: OrderStatusCreate, 
                           db: AsyncSession = Depends(get_db), 
                           current_user = Depends(get_current_admin_user)):
    created_status = await crud.create_order_status(db, status)
    return created_status

@router.get("/status/{status_id}", response_model=OrderStatusOut)
async def read_order_status(status_id: int, 
                            db: AsyncSession = Depends(get_db), 
                            current_user = Depends(get_current_admin_user)):
    status = await crud.get_order_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status

@router.get("/orders/{order_id}/status/", response_model=List[OrderStatusOut])
async def read_order_statuses(order_id: int, 
                              db: AsyncSession = Depends(get_db), 
                              current_user = Depends(get_current_user)):
    statuses = await crud.get_order_statuses(db, order_id, current_user)
    return statuses

@router.put("/status/{status_id}/", response_model=OrderStatusOut)
async def update_order_status(status_id: int, 
                              new_status: OrderStatusEnum, 
                              db: AsyncSession = Depends(get_db), 
                              current_user = Depends(get_current_admin_user)):
    updated_status = await crud.update_order_status(db, status_id, new_status)
    if not updated_status:
        raise HTTPException(status_code=404, detail="Status not found")
    return updated_status