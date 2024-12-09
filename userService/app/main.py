from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.openapi.utils import get_openapi
from app.routers import user
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

app = FastAPI(title="User Service")

# Подключаем роутеры
app.include_router(user.router, prefix="/users", tags=["Users"])

# Определяем схему безопасности
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="User Service API",
        version="1.0.0",
        description="API для управления пользователями с авторизацией",
        routes=app.routes,
    )
    
    # Определяем BearerAuth схему
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Введите токен в формате 'Bearer <токен>'",
        }
    }
    
    # Применяем схему безопасности глобально
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Настройка CORS (опционально, если требуется)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Замените на список разрешённых источников
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)