# gateway/main.py
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import httpx
from urllib.parse import urlparse
import re

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

# --- Constants ---
EXCLUDED_REQUEST_HEADERS = {'host', 'connection', 'content-length', 'accept-encoding', 'cookie', 'referer'}
EXCLUDED_RESPONSE_HEADERS = {'content-encoding', 'transfer-encoding', 'connection'}
DEFAULT_TIMEOUT = 30.0

app = FastAPI(
    title="Ecommerce Gateway",
    version="0.1.0",
    description="Bütün mikroservislərin API-lərini birləşdirən Gateway"
)

# --- Health check ---
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

# --- Əsas səhifə ---
@app.get("/")
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
    if service not in SERVICES:
        return JSONResponse({'error': 'Unknown service'}, status_code=400)

    url = f"{SERVICES[service].rstrip('/')}/{path.lstrip('/')}"
    headers = _prepare_headers(request, service)
    body = await request.body()

    query_params = dict(request.query_params)
    
    logger.info(f"Forwarding: {request.method} {url}")

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, verify=False) as client:
            resp = await client.request(
                request.method, 
                url, 
                headers=headers, 
                content=body, 
                params=query_params
            )

        resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in EXCLUDED_RESPONSE_HEADERS}
        
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=resp_headers,
            media_type=resp.headers.get("content-type"),
        )

    except httpx.RequestError as e:
        logger.error(f"RequestError: {e}")
        return JSONResponse({'error': f'Service unreachable: {e}'}, status_code=503)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse({'error': str(e)}, status_code=500)

# --- Path parametrlərini təhlil et ---
def extract_path_params(path: str):
    return re.findall(r'\{(\w+)\}', path)

# --- Dynamic Proxy Handler (YENİ VERSİYA) ---
def create_proxy_handler(service_name: str, path: str):
    path_params = extract_path_params(path)
    
    if path_params:
        # PATH PARAMETRLƏRİ OLAN ENDPOINTLƏR ÜÇÜN
        def create_handler_function(params):
            async def handler(request: Request):
                # Path parametrlərini request path-dən çıxarırıq
                formatted_path = path
                for param_name in params:
                    # Parametr dəyərini request-dən alırıq
                    param_value = request.path_params.get(param_name)
                    if param_value:
                        formatted_path = formatted_path.replace(f"{{{param_name}}}", param_value)
                
                return await forward_request(service_name, formatted_path, request)
            return handler
        
        handler_func = create_handler_function(path_params)
        
        # Funksiya adını təyin et (debug üçün)
        handler_func.__name__ = f"{service_name}_proxy_{path.replace('/', '_').replace('{', '').replace('}', '')}"
        return handler_func
        
    else:
        # PATH PARAMETRSİZ ENDPOINTLƏR ÜÇÜN
        async def handler(request: Request):
            return await forward_request(service_name, path, request)
        
        handler.__name__ = f"{service_name}_proxy_{path.replace('/', '_')}"
        return handler

# --- Load all routes from microservices ---
async def add_all_service_routes():
    for service_name, service_url in SERVICES.items():
        try:
            logger.info(f"Loading routes for {service_name} from {service_url}...")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{service_url}/openapi.json")
                if resp.status_code != 200:
                    logger.warning(f"{service_name}: OpenAPI tapılmadı ({resp.status_code})")
                    continue

                spec = resp.json()
                paths = spec.get("paths", {})
                logger.info(f"{service_name}: {len(paths)} route tapıldı")

                for path, methods in paths.items():
                    for method, operation in methods.items():
                        # YENİ: create_proxy_handler istifadə et
                        proxy_handler = create_proxy_handler(service_name, path)
                        
                        # FastAPI-ə route əlavə et
                        app.add_api_route(
                            path,
                            proxy_handler,
                            methods=[method.upper()],
                            summary=f"{service_name} → {path}",
                            tags=[service_name.capitalize()],
                            include_in_schema=True
                        )
                        
                        logger.info(f"✓ {method.upper()} {path} -> {service_name}")

        except Exception as e:
            logger.error(f"{service_name} route loading error: {e}")

# --- Startup event ---
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Ecommerce Gateway...")
    await add_all_service_routes()
    logger.info("Ecommerce Gateway started successfully")

# --- Run ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)