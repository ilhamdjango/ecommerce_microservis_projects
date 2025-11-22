# main.py
import logging
from fastapi import FastAPI, Request, Response, JSONResponse
from urllib.parse import urlparse
import httpx

from gateway.routes import analytics, shop, product, order, user, wishlist, shopcart

# --- Logging setup ---
logger = logging.getLogger("gateway")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# --- Mikroservis URL-ləri ---
SERVICES = {
    "analytics": "http://ecommerce-analytic:8000",
    "order": "http://ecommerce-order:8000",
    "product": "http://ecommerce-product:8000",
    "user": "http://ecommerce-user:8000",
    "shop": "http://ecommerce-shop:8000",
    "wishlist": "http://ecommerce-wishlist:8000",
    "shopcart": "http://ecommerce-shopcart:8000"
}

EXCLUDED_REQUEST_HEADERS = {'host', 'connection', 'content-length', 'accept-encoding', 'cookie', 'referer'}
EXCLUDED_RESPONSE_HEADERS = {'content-encoding', 'transfer-encoding', 'connection'}
DEFAULT_TIMEOUT = 30.0

app = FastAPI(title="Ecommerce Gateway", version="0.1.0", description="Bütün mikroservislərin API-lərini birləşdirən Gateway")

# --- Health check ---
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Ecommerce Gateway API", "status": "running"}

# --- Prepare headers ---
def _prepare_headers(request: Request, service: str):
    headers = {k.lower(): v for k, v in request.headers.items() if k.lower() not in EXCLUDED_REQUEST_HEADERS}
    auth_header = request.headers.get('Authorization')
    if auth_header:
        headers['authorization'] = auth_header
    user = getattr(request.state, 'user', None)
    if user:
        user_id = user.get('sub') or user.get('user_id')
        if user_id:
            headers['x-user-id'] = str(user_id)
    parsed = urlparse(SERVICES[service])
    headers['host'] = parsed.netloc
    return headers

# --- Forward request ---
async def forward_request(service: str, path: str, request: Request):
    url = f"{SERVICES[service].rstrip('/')}/{path.lstrip('/')}"
    headers = _prepare_headers(request, service)
    body = await request.body()
    query_params = dict(request.query_params)
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, verify=False) as client:
            resp = await client.request(request.method, url, headers=headers, content=body, params=query_params)
        resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in EXCLUDED_RESPONSE_HEADERS}
        return Response(content=resp.content, status_code=resp.status_code, headers=resp_headers, media_type=resp.headers.get("content-type"))
    except httpx.RequestError as e:
        return JSONResponse({'error': f'Service unreachable: {e}'}, status_code=503)
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)

# --- Include all routers ---
app.include_router(analytics.router)
app.include_router(shop.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(user.router)
app.include_router(wishlist.router)
app.include_router(shopcart.router)

# --- Run ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
