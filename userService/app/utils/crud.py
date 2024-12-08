from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import models
from app.schemas import schemas

# Регистрация нового пользователя
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = generate_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, 
                          password_hash=hashed_password, address=user.address)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Получение пользователя по ID
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalars().first()

# Получение пользователя по username
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).filter(models.User.username == username))
    return result.scalars().first()

# Проверка пароля
def verify_password(plain_password: str, hashed_password: str):
    return check_password_hash(hashed_password, plain_password)