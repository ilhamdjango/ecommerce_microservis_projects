from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_gateway_starts():
    response = client.get("/")
    # Əgər root endpoint yoxdursa, 404 qaytaracaq, o da normaldır
    assert response.status_code in [200, 404]