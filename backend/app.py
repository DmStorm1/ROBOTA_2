from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import feedparser
import config
from config import STUDENT_ID, ROOM_ID

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

# --- Stores ---
store = {}
news_store = {}
draw_store = {}  # для зберігання малюнків по room_id

# --- Fake users for demo ---
fake_users_db = {
    STUDENT_ID: {
        "username": STUDENT_ID,
        "full_name": STUDENT_ID,
        "hashed_password": "password123",  # лише для тестування
        "disabled": False,
    }
}

# --- Startup: автозавантаження джерел ---
@app.on_event("startup")
async def load_initial_sources() -> None:
    student_id = getattr(config, "STUDENT_ID", None)
    sources    = getattr(config, "SOURCES", [])
    if student_id and isinstance(sources, list):
        store[student_id] = list(sources)
        news_store[student_id] = []
        draw_store[ROOM_ID] = []
        print(f"[startup] loaded {len(sources)} feeds for {student_id}")
        print(f"[startup] initialized draw_store for {ROOM_ID}")

# --- Аналізатор ---
analyzer = SentimentIntensityAnalyzer()

# --- Моделі ---
class SourcePayload(BaseModel):
    url: str

class DrawCommand(BaseModel):
    x: int
    y: int
    type: str

class FilterPayload(BaseModel):
    image_data: list
    filter_name: str

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

# --- Draw API ---
@app.post("/draw/{room_id}")
def draw(room_id: str, cmd: DrawCommand):
    if room_id not in draw_store:
        draw_store[room_id] = []
    draw_store[room_id].append(cmd.dict())
    return {"status": "ok"}

@app.get("/draw/{room_id}")
def get_draw(room_id: str):
    if room_id not in draw_store:
        raise HTTPException(status_code=404, detail="Room not found")
    return draw_store[room_id]

# --- Filter API ---
@app.post("/filter/{room_id}")
def apply_filter(room_id: str, payload: FilterPayload):
    # Просто повернемо ті ж дані для тесту
    if room_id not in draw_store:
        draw_store[room_id] = []  # ініціалізація, щоб не було 404
    # Для простоти - повертаємо image_data без змін
    return {"image_data": payload.image_data}

