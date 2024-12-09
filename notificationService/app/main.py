from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from app.models import models
from app.dependencies import engine
from app.routers import notification

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(notification.router, prefix="/notifications", tags=["Notifications"])

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Notification Service API",
        version="1.0.0",
        description="API для отслеживания обновлений статуса заказа",
        routes=app.routes,
    )
    
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
    
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)