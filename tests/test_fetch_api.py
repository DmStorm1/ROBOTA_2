from fastapi.testclient import TestClient
from backend.app import app, news_store, sources_store
from config import STUDENT_ID
import feedparser

client = TestClient(app)

def test_get_news_empty():
    sources_store[STUDENT_ID] = []      # Додаємо пустий список джерел
    news_store[STUDENT_ID] = []         # Порожні новини
    res = client.get(f"/news/{STUDENT_ID}")
    assert res.status_code == 200
    assert res.json() == {"articles": []}

def test_get_empty_sources():
    sources_store[STUDENT_ID] = []      # Ініціалізуємо пустий список джерел
    res = client.get(f"/sources/{STUDENT_ID}")
    assert res.status_code == 200
    assert res.json() == {"sources": []}

# Dummy RSS feed для підміни feedparser.parse
class DummyFeed:
    entries = [
        {"title": "T1", "link": "http://a", "published": "2025-01-01"},
        {"title": "T2", "link": "http://b", "published": ""}
    ]

def test_fetch_and_get(monkeypatch):
    monkeypatch.setattr("config.SOURCES", ["http://example.com/rss"])
    monkeypatch.setattr(feedparser, "parse", lambda url: DummyFeed)

    sources_store[STUDENT_ID] = ["http://example.com/rss"]   # Ініціалізуємо джерела для студента
    news_store[STUDENT_ID] = []                               # Очищаємо новини

    res1 = client.post(f"/fetch/{STUDENT_ID}")
    assert res1.status_code == 200
    assert res1.json() == {"fetched": 2}

    res2 = client.get(f"/news/{STUDENT_ID}")
    assert res2.status_code == 200
    assert res2.json() == {
        "articles": [
            {"title": "T1", "link": "http://a", "published": "2025-01-01"},
            {"title": "T2", "link": "http://b", "published": ""}
        ]
    }
