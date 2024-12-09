from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class OrderStatusEnum(str, Enum):
    preparing = "preparing"
    ready_waiting_for_courier = "ready_waiting_for_courier"
    on_the_way = "on_the_way"
    closed = "closed"

class OrderStatusCreate(BaseModel):
    order_id: int
    status: OrderStatusEnum

class OrderStatusOut(BaseModel):
    id: int
    order_id: int
    status: OrderStatusEnum
    timestamp: datetime

    class Config:
        from_attributes = True