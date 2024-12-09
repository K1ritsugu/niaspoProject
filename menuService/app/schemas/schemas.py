from pydantic import BaseModel
from typing import Optional


# Базовая схема для блюда
class DishBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None


# Схема для создания блюда
class DishCreate(DishBase):
    pass


# Схема для обновления блюда (опциональные поля)
class DishUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None


# Схема для возвращаемых данных блюда
class DishOut(DishBase):
    id: int

    class Config:
        from_attributes = True


# Схема для пользователей
class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True
