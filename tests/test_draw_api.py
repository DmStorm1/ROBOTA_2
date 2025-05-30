from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)
ROOM_ID = "room-1"  # або інший

def test_draw_and_get():
    cmd = {"x": 5, "y": 5, "type": "line"}
    res = client.post(f"/draw/{ROOM_ID}", json=cmd)
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    res2 = client.get(f"/draw/{ROOM_ID}")
    assert res2.status_code == 200
    assert cmd in res2.json()
