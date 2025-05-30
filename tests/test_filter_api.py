from fastapi.testclient import TestClient
from backend.app import app
from config import STUDENT_ID

client = TestClient(app)

def test_filter_api():
    payload = {"image_data": [1,2,3], "filter_name": "blur"}
    res = client.post(f"/filter/{STUDENT_ID}", json=payload)
    assert res.status_code == 404 and res.json()["image_data"] == payload["image_data"]
