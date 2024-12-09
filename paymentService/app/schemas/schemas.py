from pydantic import BaseModel, conlist, field_validator
from datetime import datetime
from typing import List, Optional

class OrderItem(BaseModel):
    dish_id: int
    amount: int

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItem]
    transaction_id: int
    payment_method: str

    @field_validator('items')
    def validate_items(cls, v):
        if len(v) < 1:
            raise ValueError("items must contain at least one OrderItem")
        return v

    @field_validator('payment_method')
    def validate_payment_method(cls, v):
        if v not in ['cash', 'card']:
            raise ValueError("payment_method must be 'cash' or 'card'")
        return v

class OrderOut(BaseModel):
    id: int
    transaction_id: int
    user_id: int
    items: List[OrderItem]
    status: str
    created_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    user_id: int
    amount: float
    payment_method: str

    @field_validator('payment_method')
    def validate_payment_method(cls, v):
        if v not in ['cash', 'card']:
            raise ValueError("payment_method must be 'cash' or 'card'")
        return v

class TransactionOut(BaseModel):
    id: int
    user_id: int
    amount: float
    payment_method: str
    status: str
    created_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True