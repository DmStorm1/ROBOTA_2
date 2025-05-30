from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)
ROOM_ID = "room-1"  # або будь-який інший ідентифікатор

def test_filter_api():
    payload = {"image_data": [1, 2, 3], "filter_name": "blur"}
    res = client.post(f"/filter/{ROOM_ID}", json=payload)
    assert res.status_code == 200
    assert res.json()["image_data"] == payload["image_data"]
