import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
from dotenv import load_dotenv

load_dotenv()

# URL подключения к базе данных
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем асинхронную сессию
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, autocommit=False, autoflush=False
)

# Асинхронная зависимость для получения сессии
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session