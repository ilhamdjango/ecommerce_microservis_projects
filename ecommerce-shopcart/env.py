DEBUG=True
ENV=production

# Database configuration - COMPOSE-DAKI KIMI
DB_HOST=db-shopcart
DB_PORT=5432
DB_NAME=shopcart_db
DB_USER=shopcart_user
DB_PASSWORD=12345

# Full SQLAlchemy URL
DATABASE_URL=postgresql+psycopg2://shopcart_user:12345@db-shopcart:5432/shopcart_db

# FastAPI secret key
SECRET_KEY=d4a18b05f4a744a6a2d9981c57cb07a635fe01912c994e5f68b4db7b6b6a7f2d

# App port - CONTAINER DAXILINDAKI PORT
PORT=8000