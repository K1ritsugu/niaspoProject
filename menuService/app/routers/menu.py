from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app import dependencies
from app.utils import crud
from app.schemas import schemas
from pathlib import Path

router = APIRouter()

@router.post("/dishes/", response_model=schemas.DishOut)
async def create_dish(
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: dict = Depends(dependencies.get_current_admin_user),
):
    try:
        # Сохранение изображения
        image_path = Path("images") / image.filename
        image_path.parent.mkdir(parents=True, exist_ok=True)
        with open(image_path, "wb") as buffer:
            buffer.write(image.file.read())

        dish_data = schemas.DishCreate(
            name=name,
            description=description,
            price=price,
            image_url=str(image_path),
        )
        created_dish = await crud.create_dish(db=db, dish=dish_data)
        if not created_dish:
            raise HTTPException(status_code=400, detail="Failed to create dish")
        return created_dish

    except IntegrityError:
        raise HTTPException(status_code=400, detail=f"Dish with name '{name}' already exists.")

@router.get("/dishes/{dish_id}", response_model=schemas.DishOut)
async def read_dish(dish_id: int, db: AsyncSession = Depends(dependencies.get_db)):
    db_dish = await crud.get_dish(db, dish_id=dish_id)
    if db_dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    return db_dish

@router.get("/dishes/", response_model=list[schemas.DishOut])
async def read_dishes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(dependencies.get_db)
):
    dishes = await crud.get_dishes(db, skip=skip, limit=limit)
    if not dishes:
        raise HTTPException(status_code=404, detail="No dishes found")
    return dishes

@router.put("/dishes/{dish_id}", response_model=schemas.DishOut)
async def update_dish(
    dish_id: int,
    dish_update: str = Form(...),  # Принимаем строку JSON в форме
    db: AsyncSession = Depends(dependencies.get_db),
    image: UploadFile = File(None),
    current_user: dict = Depends(dependencies.get_current_admin_user),
):
    try:
        dish_update_data = schemas.DishUpdate.parse_raw(dish_update)

        db_dish = await crud.get_dish(db, dish_id=dish_id)
        if db_dish is None:
            raise HTTPException(status_code=404, detail="Dish not found")

        if image:
            image_path = Path("images") / image.filename
            image_path.parent.mkdir(parents=True, exist_ok=True)
            with open(image_path, "wb") as buffer:
                buffer.write(image.file.read())
            dish_update_data.image_url = str(image_path)

        updated_dish = await crud.update_dish(db=db, dish_id=dish_id, dish_update=dish_update_data)
        if not updated_dish:
            raise HTTPException(status_code=400, detail="Failed to update dish")

        return updated_dish

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Dish name already exists.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/dishes/{dish_id}", response_model=dict)
async def delete_dish(
    dish_id: int, 
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: dict = Depends(dependencies.get_current_admin_user),
):
    db_dish = await crud.get_dish(db, dish_id=dish_id)
    
    if db_dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")

    # Удаляем блюдо
    result = await crud.delete_dish(db=db, dish_id=dish_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete dish")
    return {"message": "Dish deleted successfully"}