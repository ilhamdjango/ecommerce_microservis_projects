#!/bin/bash
set -e

echo "=== WISHLIST ENTRYPOINT ==="

# 1. ✅ ƏSAS TEST: MAIN.PY İŞLƏYİR?
echo "?? Testing main.py..."
python -c "
try:
    from app.main import app
    print('? ✅ MAIN.PY IMPORT OLUNDU!')
    
    # ROUTE-LARI GÖSTER
    routes = [route.path for route in app.routes if hasattr(route, 'path')]
    print(f'? 📍 Mövcud routes: {routes}')
    
    # ENDPOINT SAYI
    endpoint_count = len([r for r in app.routes if hasattr(r, 'methods')])
    print(f'? 🔢 Toplam endpoint: {endpoint_count}')
    
except Exception as e:
    print(f'? ❌ MAIN.PY XƏTASI: {e}')
    print('? 💡 Problem: Router import, path, ya da dependency')
    exit(1)
"

# 2. ✅ DATABASE TEST
echo "?? Testing database..."
python -c "
from app.database import engine
try:
    with engine.connect() as conn:
        print('? ✅ Database is reachable')
except Exception as e:
    print(f'? ❌ Database error: {e}')
    exit(1)
"

# 3. ✅ MIGRATIONS
echo "?? Running migrations..."
alembic upgrade head

# 4. ✅ START SERVICE
echo "?? Starting Wishlist Service..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000