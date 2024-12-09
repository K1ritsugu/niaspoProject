import os
import httpx
from fastapi import HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from app.models.models import User
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8000")

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, autocommit=False, autoflush=False
)

security = HTTPBearer()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def validate_token_and_get_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Проверяет токен через user_service и возвращает данные о пользователе, если токен валиден.
    """
    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{USER_SERVICE_URL}/users/me/",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()  # Возвращает данные пользователя
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid token")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User service unavailable")
        
async def get_user(db: AsyncSession, user_id: int):

    result = await db.execute(select(User).filter(User.id == user_id))
    result = result.scalars().first()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    return result


async def get_current_user(current_user: dict = Depends(validate_token_and_get_user)):
    return current_user

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Insufficient rights")
    return current_user