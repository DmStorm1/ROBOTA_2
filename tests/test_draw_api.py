from fastapi.testclient import TestClient
from backend.app import app
from config import STUDENT_ID

client = TestClient(app)

def test_draw_and_get():
    cmd = {"x": 5, "y": 5, "type": "line"}
    res = client.post(f"/draw/{STUDENT_ID}", json=cmd)
    assert res.status_code == 200 and res.json()["status"] == "ok"
    res2 = client.get(f"/draw/{STUDENT_ID}")
    assert res2.status_code == 200 and cmd in res2.json()
