FROM python:3.12-slim

WORKDIR /app

# Sistem asılılıqları
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pip upgrade
RUN pip install --upgrade pip

# Asılılıqlar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bütün faylları kopyala (gateway qovluğu da daxil)
COPY . .

EXPOSE 8000
# ƏSAS DƏYİŞİKLİK BURADA:
CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]