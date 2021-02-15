from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)


# Test template returns
# TemplateNotFound Error

# def test_home():
#     response = client.get('/')
#     assert response.status_code == 200
