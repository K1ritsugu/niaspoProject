from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app import dependencies
from app.utils import crud
from app.schemas import schemas
from datetime import timedelta

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(dependencies.get_db)
):
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=dependencies.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = dependencies.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")

@router.post("/registration/", response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(dependencies.get_db)):
    if user.role and user.role == 'admin':
        raise HTTPException(status_code=403, detail="Недостаточно прав для создания администратора")
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь уже зарегистрирован")
    return await crud.create_user(db=db, user=user)

@router.post("/admin/registration/", response_model=schemas.UserOut)
async def create_admin_user(
    admin_user: schemas.AdminUserCreate,
    db: AsyncSession = Depends(dependencies.get_db)
):
    if admin_user.admin_secret != dependencies.ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Неверный секретный ключ")
    admin_user.role = 'admin'
    db_user = await crud.get_user_by_username(db, username=admin_user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь уже зарегистрирован")
    return await crud.create_user(db=db, user=admin_user)

@router.get("/me/", response_model=schemas.UserOut)
async def read_users_me(current_user: schemas.UserOut = Depends(dependencies.get_current_user)):
    return current_user