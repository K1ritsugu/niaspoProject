import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from app.models import models
from app.schemas import schemas

# CRUD для получения блюда по ID
async def get_dish(db: AsyncSession, dish_id: int):
    query = select(models.Dish).where(models.Dish.id == dish_id)
    result = await db.execute(query)
    return result.scalars().first()


async def get_dishes(db: AsyncSession, skip: int = 0, limit: int = 10):
    # Запрос для получения блюд с пагинацией
    dishes_query = select(models.Dish).offset(skip).limit(limit)
    result = await db.execute(dishes_query)
    dishes = result.scalars().all()
    
    # Запрос для подсчёта общего количества блюд
    count_query = select(func.count()).select_from(models.Dish)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    return {"dishes": dishes, "total": total}



# CRUD для создания блюда
async def create_dish(db: AsyncSession, dish: schemas.DishCreate):
    new_dish = models.Dish(**dish.dict())
    db.add(new_dish)
    await db.commit()
    await db.refresh(new_dish)
    return new_dish


# CRUD для обновления блюда
async def update_dish(db: AsyncSession, dish_id: int, dish_update: dict):
    query = select(models.Dish).where(models.Dish.id == dish_id)
    result = await db.execute(query)
    db_dish = result.scalars().first()
    if not db_dish:
        return None
    for key, value in dish_update.items():
        setattr(db_dish, key, value)
    await db.commit()
    await db.refresh(db_dish)
    return db_dish


# CRUD для удаления блюда
async def delete_dish(db: AsyncSession, dish_id: int):
    query = select(models.Dish).where(models.Dish.id == dish_id)
    result = await db.execute(query)
    db_dish = result.scalars().first()
    os.remove(db_dish.image_url)
    if not db_dish:
        return None
    await db.delete(db_dish)
    await db.commit()
    return True
