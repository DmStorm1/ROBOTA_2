from fastapi.testclient import TestClient
from backend.app import app, news_store
from config import STUDENT_ID
import vaderSentiment.vaderSentiment as vs

client = TestClient(app)

def test_analyze_empty():
    news_store[STUDENT_ID] = []
    res = client.post(f"/analyze/{STUDENT_ID}")
    assert res.status_code == 404
    assert res.json() == {"analyzed": 0, "articles": []}

def test_analyze_real(monkeypatch):
    news_store[STUDENT_ID] = [
        {"title": "I love this", "link": "u1", "published": ""},
        {"title": "I hate that", "link": "u2", "published": ""}
    ]

    class FakeAnalyzer:
        def polarity_scores(self, txt):
            if "love" in txt:
                return {"neg": 0.0, "neu": 0.3, "pos": 0.7, "compound": 0.8}
            elif "hate" in txt:
                return {"neg": 0.6, "neu": 0.4, "pos": 0.0, "compound": -0.6}
            else:
                return {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0}

    # Підміна SentimentIntensityAnalyzer, який створюється в app.py
    monkeypatch.setattr(vs, "SentimentIntensityAnalyzer", lambda: FakeAnalyzer())

    # Імітуємо повторне створення аналізатора, як у app.py
    from backend import app as backend_app
    backend_app.analyzer = vs.SentimentIntensityAnalyzer()

    res = client.post(f"/analyze/{STUDENT_ID}")
    assert res.status_code == 404
    data = res.json()
    assert data["analyzed"] == 2
    articles = data["articles"]

    assert articles[0]["title"] == "I love this"
    assert articles[0]["sentiment"] == "positive"
    assert "compound" in articles[0]["scores"]

    assert articles[1]["title"] == "I hate that"
    assert articles[1]["sentiment"] == "negative"
    assert "compound" in articles[1]["scores"]
