import logging
import httpx
from fastapi import Request
from fastapi.responses import JSONResponse, Response
from urllib.parse import urlparse

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

# --- Forward request (production-ready) ---
async def forward_request(service: str, path: str, request: Request):
    if service not in SERVICES:
        return JSONResponse({'error': 'Unknown service'}, status_code=400)

    url = f"{SERVICES[service].rstrip('/')}/{path.lstrip('/')}"
    headers = _prepare_headers(request, service)
    body = await request.body()

    logger.info(f"Forwarding request to {url} | Method: {request.method}")

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, verify=False) as client:
            # ✅ params=None saxlayaraq query param əlavə etmədən göndəririk
            resp = await client.request(
                request.method,
                url,
                headers=headers,
                content=body,
                params=None
            )

        resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in EXCLUDED_RESPONSE_HEADERS}
        logger.info(f"Received {resp.status_code} from {url}")

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

# --- Prepare headers (with auth and user forwarding) ---
def _prepare_headers(request: Request, service: str):
    headers = {k.lower(): v for k, v in request.headers.items() if k.lower() not in EXCLUDED_REQUEST_HEADERS}

    auth_header = request.headers.get('Authorization')
    if auth_header:
        headers['authorization'] = auth_header
        logger.info(f"Forwarding with Authorization header")
    else:
        logger.warning("No Authorization header found")

    user = getattr(request.state, 'user', None)
    if user:
        user_id = user.get('sub') or user.get('user_id')
        if user_id:
            headers['x-user-id'] = str(user_id)
            logger.info(f"Forwarding with X-User-ID: {user_id}")
        else:
            logger.warning("User ID not found in request.state.user")
    else:
        logger.warning("No user in request.state, X-User-ID not set")

    parsed = urlparse(SERVICES[service])
    headers['host'] = parsed.netloc

    return headers

# --- Proxy with path params ---
def create_proxy_with_params(service_url: str, path_template: str):
    async def proxy(request: Request, **kwargs):
        path = path_template.format(**kwargs)
        service = next((s for s, url in SERVICES.items() if url == service_url), None)
        return await forward_request(service, path, request)
    return proxy

# --- Proxy without path params ---
def create_proxy_without_params(service_url: str, path: str):
    async def proxy(request: Request):
        service = next((s for s, url in SERVICES.items() if url == service_url), None)
        return await forward_request(service, path, request)
    return proxy
