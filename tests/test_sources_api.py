from fastapi.testclient import TestClient
from backend.app import app, sources_store
from config import STUDENT_ID

client = TestClient(app)

def test_get_empty_sources():
    # Очистити sources_store для STUDENT_ID, щоб не було старих даних
    sources_store[STUDENT_ID] = []
    
    res = client.get(f"/sources/{STUDENT_ID}")
    assert res.status_code == 200
    assert res.json() == {"sources": []}

def test_add_and_get_source():
    url = "https://example.com/rss"  # без < і >
    
    # Очистити перед тестом
    sources_store[STUDENT_ID] = []
    
    res1 = client.post(f"/sources/{STUDENT_ID}", json={"url": url})
    assert res1.status_code == 200
    assert url in res1.json()["sources"]
    
    res2 = client.get(f"/sources/{STUDENT_ID}")
    assert res2.status_code == 200
    assert res2.json()["sources"] == [url]
