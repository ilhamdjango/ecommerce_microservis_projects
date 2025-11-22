# gateway/openapi.py
import httpx
import asyncio
from fastapi.openapi.utils import get_openapi
from gateway.services import SERVICE_URLS


async def fetch_openapi(url: str):
    """Mikroservisdən OpenAPI sənədini fetch edir"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{url}/openapi.json")
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        # Logging istifadə etmək olar, amma minimal versiyada pass
        return None

async def merge_openapi_docs(app):
    """Bütün mikroservislərin OpenAPI sənədlərini birləşdirir"""
    merged_paths = {}
    merged_schemas = {}

    # Bütün servislərin openapi.json fayllarını parallel fetch edirik
    results = await asyncio.gather(*[fetch_openapi(url) for url in SERVICE_URLS.values()])

    for service_name, data in zip(SERVICE_URLS.keys(), results):
        if not data:
            continue

        # paths birləşdiririk
        for path, path_item in data.get("paths", {}).items():
            if path not in merged_paths:
                merged_paths[path] = {}
            for method, op in path_item.items():
                merged_paths[path][method] = op
                # Mikroservis adını tag kimi əlavə edirik
                merged_paths[path][method]["tags"] = [service_name.capitalize()]

        # components.schemas birləşdiririk
        components = data.get("components", {})
        if "schemas" in components:
            merged_schemas.update(components["schemas"])

    # FastAPI üçün OpenAPI schema yaradırıq
    app.openapi_schema = get_openapi(
        title="Ecommerce Gateway",
        version="1.0.0",
        description="Bütün mikroservislərin birləşmiş OpenAPI sənədi",
        routes=app.routes,
    )

    # paths əlavə edirik
    app.openapi_schema["paths"].update(merged_paths)

    # components.schemas əlavə edirik
    if "components" not in app.openapi_schema:
        app.openapi_schema["components"] = {}
    app.openapi_schema["components"]["schemas"] = merged_schemas

async def setup_openapi(app):
    """Startup zamanı çağırılacaq"""
    await merge_openapi_docs(app)
