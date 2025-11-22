FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ✅ ENTRYPOINT SCRIPTINI DÜZƏLT VƏ İŞLƏT
RUN sed -i 's/\r$//' entrypoint-new.sh && chmod +x entrypoint-new.sh
CMD ["./entrypoint-new.sh"]