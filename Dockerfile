# 1️⃣ Базовый образ с Python
FROM python:3.10-slim

# 2️⃣ Рабочая директория внутри контейнера
WORKDIR /app

# 3️⃣ Скопируем зависимости (если есть)
COPY requirements.txt .

# 4️⃣ Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Копируем всё приложение внутрь контейнера
COPY . .

# 6️⃣ Открываем порт 8181
EXPOSE 8181

# 7️⃣ Запускаем сервер, как в systemd unit
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]