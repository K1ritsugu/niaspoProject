import httpx
import asyncio
import os
from fastapi import FastAPI, APIRouter, Request, Response, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse


app = FastAPI(title="Gateway Service")

# Базовые URL микросервисов
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL")

# Роутеры для разных микросервисов
user_router = APIRouter(prefix="/users", tags=["Users"])
menu_router = APIRouter(prefix="/menu", tags=["Menu"])
payment_router = APIRouter(prefix="/payments", tags=["Payments"])
notification_router = APIRouter(prefix="/notifications", tags=["Notifications"])

async def get_remote_openapi(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{url}/openapi.json")
        response.raise_for_status()
        return response.json()

@app.on_event("startup")
async def merge_openapi_specs():
    specs = []
    service_urls = [
        USER_SERVICE_URL,
        MENU_SERVICE_URL,
        PAYMENT_SERVICE_URL,
        NOTIFICATION_SERVICE_URL,
    ]
    for url in service_urls:
        for attempt in range(5):
            try:
                spec = await get_remote_openapi(url)
                specs.append(spec)
                break
            except httpx.RequestError as e:
                print(f"Warning: Attempt {attempt + 1} failed to fetch OpenAPI spec from {url}: {e}")
                await asyncio.sleep(2) 
        else:
            print(f"Error: Could not fetch OpenAPI spec from {url} after multiple attempts.")

    merged_paths = {}
    merged_components = {"schemas": {}, "securitySchemes": {}}

    for spec in specs:
        # Merge paths
        for path, methods in spec.get("paths", {}).items():
            merged_paths[path] = methods

        # Merge schemas
        schemas = spec.get("components", {}).get("schemas", {})
        merged_components["schemas"].update(schemas)

        # Merge security schemes
        security_schemes = spec.get("components", {}).get("securitySchemes", {})
        merged_components["securitySchemes"].update(security_schemes)

    app.openapi_schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "Gateway API",
            "version": "1.0.0",
        },
        "paths": merged_paths,
        "components": merged_components,
    }

@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    return JSONResponse(app.openapi_schema)

@app.get("/docs", include_in_schema=False)
async def overridden_swagger():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Gateway API Docs")

# Функция для проксирования запросов
async def proxy(request: Request, service_url: str, path: str):
    async with httpx.AsyncClient() as client:
        try:
            # Log the proxied request details
            print(f"Proxying {request.method} request to: {service_url}/{path}")
            
            # Existing proxy logic...
            headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
            params = dict(request.query_params)
            
            # Handling multipart/form-data
            if request.headers.get("content-type", "").startswith("multipart/form-data"):
                form = await request.form()
                data = {}
                files = []
                for field, value in form.multi_items():
                    if hasattr(value, "filename"):
                        files.append((field, (value.filename, await value.read(), value.content_type)))
                    else:
                        data[field] = value
                
                response = await client.request(
                    method=request.method,
                    url=f"{service_url}/{path}",
                    headers=headers,
                    params=params,
                    data=data,
                    files=files,
                )
            else:
                body = await request.body()
                response = await client.request(
                    method=request.method,
                    url=f"{service_url}/{path}",
                    headers=headers,
                    params=params,
                    content=body,
                )
            
            # Log the response status
            print(f"Received response with status: {response.status_code},GGGG {service_url}/{path}")
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={key: value for key, value in response.headers.items() if key.lower() != 'content-encoding'},
            )
        except httpx.RequestError as e:
            print(f"Request error while proxying to {service_url}/{path}: {e}")
            raise HTTPException(status_code=503, detail="Service Unavailable")

# Маршруты для User Service
@user_router.post("/registration/")
async def create_user(request: Request):
    print(request)
    return await proxy(request, USER_SERVICE_URL, "users/registration/")

@user_router.post("/admin/registration/")
async def create_admin_user(request: Request):
    return await proxy(request, USER_SERVICE_URL, "users/admin/registration/")

@user_router.post("/token")
async def login_for_access_token(request: Request):
    return await proxy(request, USER_SERVICE_URL, "users/token")

@user_router.get("/users/me")
async def read_users_me(request: Request):
    return await proxy(request, USER_SERVICE_URL, "users/me/")

# Маршруты для Menu Service
@menu_router.post("/dishes/")
async def create_dish(request: Request):
    return await proxy(request, MENU_SERVICE_URL, "menu/dishes/")

@menu_router.get("/dishes/{dish_id}")
async def read_dish(request: Request, dish_id: int):
    return await proxy(request, MENU_SERVICE_URL, f"menu/dishes/{dish_id}")

@menu_router.get("/dishes/")
async def read_dishes(request: Request):
    return await proxy(request, MENU_SERVICE_URL, "menu/dishes/")

@menu_router.put("/dishes/{dish_id}")
async def update_dish(request: Request, dish_id: int):
    return await proxy(request, MENU_SERVICE_URL, f"menu/dishes/{dish_id}")

@menu_router.delete("/dishes/{dish_id}")
async def delete_dish(request: Request, dish_id: int):
    return await proxy(request, MENU_SERVICE_URL, f"menu/dishes/{dish_id}")

# Маршруты для Payment Service
@payment_router.post("/pay/")
async def process_payment(request: Request):
    return await proxy(request, PAYMENT_SERVICE_URL, "payments/pay/")

@payment_router.get("/pay/{transaction_id}")
async def read_transaction(request: Request, transaction_id: int):
    return await proxy(request, PAYMENT_SERVICE_URL, f"payments/pay/{transaction_id}")

@payment_router.get("/pay/")
async def read_transactions(request: Request):
    return await proxy(request, PAYMENT_SERVICE_URL, "payments/pay/")

@payment_router.post("/orders/")
async def create_order(request: Request):
    return await proxy(request, PAYMENT_SERVICE_URL, "payments/orders/")

@payment_router.get("/orders/{order_id}")
async def read_order(request: Request, order_id: int):
    return await proxy(request, PAYMENT_SERVICE_URL, f"payments/orders/{order_id}")

@payment_router.get("/orders/")
async def read_orders(request: Request):
    return await proxy(request, PAYMENT_SERVICE_URL, "payments/orders/")

@payment_router.put("/orders/{order_id}/status/")
async def update_order_status(request: Request, order_id: int):
    return await proxy(request, PAYMENT_SERVICE_URL, f"payments/orders/{order_id}/status/")

# Маршруты для Notification Service
@notification_router.post("/status/")
async def add_order_status(request: Request):
    return await proxy(request, NOTIFICATION_SERVICE_URL, "notifications/status/")

@notification_router.get("/status/{status_id}")
async def read_order_status(request: Request, status_id: int):
    return await proxy(request, NOTIFICATION_SERVICE_URL, f"notifications/status/{status_id}")

@notification_router.get("/orders/{order_id}/status/")
async def read_order_statuses(request: Request, order_id: int):
    return await proxy(request, NOTIFICATION_SERVICE_URL, f"notifications/orders/{order_id}/status/")

@notification_router.put("/status/{status_id}/")
async def update_order_status(request: Request, status_id: int):
    return await proxy(request, NOTIFICATION_SERVICE_URL, f"notifications/status/{status_id}/")

# Подключаем роутеры к приложению
app.include_router(user_router)
app.include_router(menu_router)
app.include_router(payment_router)
app.include_router(notification_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)