from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import feedparser
import config
from config import STUDENT_ID
from contextlib import asynccontextmanager

app = FastAPI()

# --- CORS ---
origins = [
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Store ---
store = {}
news_store = {}
fake_users_db = {
    STUDENT_ID: {
        "username": STUDENT_ID,
        "full_name": STUDENT_ID,
        "hashed_password": "password123",  # лише для тестування
        "disabled": False,
    }
}

# --- Lifespan: заміна @app.on_event("startup") ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Завантаження початкових джерел при запуску
    student_id = getattr(config, "STUDENT_ID", None)
    sources = getattr(config, "SOURCES", [])
    if student_id and isinstance(sources, list):
        store[student_id] = list(sources)
        news_store[student_id] = []
        print(f"[lifespan startup] loaded {len(sources)} feeds for {student_id}")
    yield
    # Тут можна додати код для "shutdown", якщо потрібно

app = FastAPI(lifespan=lifespan)

# --- Аналізатор ---
analyzer = SentimentIntensityAnalyzer()

# --- Модель ---
class SourcePayload(BaseModel):
    url: str

# --- Джерела ---
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

# --- Завантаження новин ---
@app.post("/fetch/{student_id}")
def fetch_news(student_id: str):
    if student_id not in store:
        raise HTTPException(status_code=404, detail="Student not found")

    news_store[student_id] = []
    fetched = 0

    for url in store.get(student_id, []):
        feed = feedparser.parse(url)
        for entry in getattr(feed, "entries", []):
            news_store[student_id].append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", "")
            })
            fetched += 1

    return {"fetched": fetched}

# --- Отримання новин ---
@app.get("/news/{student_id}")
def get_news(student_id: str):
    if student_id not in news_store:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"articles": news_store[student_id]}

# --- Аналіз тональності ---
@app.post("/analyze/{student_id}")
def analyze_tone(student_id: str):
    if student_id not in news_store:
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
