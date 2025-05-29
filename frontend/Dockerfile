# ---------- 1. Базовий образ Nginx ----------
FROM nginx:alpine

# ---------- 2. Очищаємо дефолтну статику (опційно) ----------
RUN rm -rf /usr/share/nginx/html/*

# ---------- 3. Копіюємо статичні файли фронтенду ----------
COPY frontend/ /usr/share/nginx/html/

# ---------- 4. Виставляємо порт для HTTP ----------
EXPOSE 80

# ---------- 5. Запуск Nginx у foreground ----------
CMD ["nginx", "-g", "daemon off;"]
