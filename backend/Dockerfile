# ---------- 1. Базовий образ ----------
FROM python:3.13-slim

# ---------- 2. Робоча директорія ----------
WORKDIR /app

# ---------- 3. Копіюємо залежності і встановлюємо пакети ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- 4. Копіюємо код бекенду і конфігурацію ----------
COPY backend/   ./
COPY config.py  ./

# ---------- 5. Відкриваємо порт для FastAPI ----------
EXPOSE 8000

# ---------- 6. Команда запуску ----------
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
