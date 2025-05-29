from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import config
from config import STUDENT_ID
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pydantic import BaseModel

app = FastAPI()

# ✅ Додаємо CORS для localhost та 127.0.0.1
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8001",
        "http://127.0.0.1:8001"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Пам’ять для джерел
store = {STUDENT_ID: config.SOURCES.copy()}

# Пам’ять для новин
news_store = {STUDENT_ID: []}

# Ініціалізуємо аналізатор тону
analyzer = SentimentIntensityAnalyzer()

# Pydantic модель для POST /sources
class SourcePayload(BaseModel):
    url: str

@app.get("/sources/{student_id}")
def get_sources(student_id: str):
    if student_id not in store:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"sources": store[student_id]}

@app.post("/sources/{student_id}")
def add_source(student_id: str, payload: SourcePayload):
    if student_id not in store:
        store[student_id] = []

    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    if url in store[student_id]:
        raise HTTPException(status_code=400, detail="URL already exists")

    store[student_id].append(url)
    return {"sources": store[student_id]}

@app.post("/fetch/{student_id}")
def fetch_news(student_id: str):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")
    
    news_store[student_id].clear()
    fetched = 0

    for url in config.SOURCES:
        feed = feedparser.parse(url)
        for entry in getattr(feed, "entries", []):
            news_store[student_id].append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", "")
            })
            fetched += 1

    return {"fetched": fetched}

@app.get("/news/{student_id}")
def get_news(student_id: str):
    if student_id not in news_store:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"articles": news_store[student_id]}

@app.post("/analyze/{student_id}")
def analyze_tone(student_id: str):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")
    
    articles = news_store.get(student_id, [])
    result = []

    for art in articles:
        text = art.get("title", "")
        scores = analyzer.polarity_scores(text)
        comp = scores["compound"]
        if comp >= 0.05:
            label = "positive"
        elif comp <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        result.append({**art, "sentiment": label, "scores": scores})
    
    return {"analyzed": len(result), "articles": result}
