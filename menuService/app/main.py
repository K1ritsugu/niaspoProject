from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.models import models
from app.dependencies import engine
from app.routers import menu
from fastapi.openapi.utils import get_openapi

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

# Указываем папку для хранения изображений
app.mount("/images", StaticFiles(directory="images"), name="images")

# Подключаем роутеры
app.include_router(menu.router)

# Настройка OpenAPI для поддержки Bearer Auth
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Menu Service API",
        version="1.0.0",
        description="API для управления блюдами с авторизацией",
        routes=app.routes,
    )
    # Добавляем схему безопасности BearerAuth как словарь
    security_scheme = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Введите токен в формате 'Bearer <токен>'",
        }
    }
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}
    openapi_schema["components"]["securitySchemes"].update(security_scheme)
    # Применяем схему безопасности глобально
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)