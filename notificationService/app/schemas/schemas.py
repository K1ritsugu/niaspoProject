from pydantic import BaseModel
from datetime import datetime

class OrderStatusCreate(BaseModel):
    order_id: int
    status: str

class OrderStatusOut(BaseModel):
    id: int
    order_id: int
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True