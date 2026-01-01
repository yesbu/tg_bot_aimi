# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для работы с изображениями (Pillow)
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем директорию для базы данных (если нужно)
RUN mkdir -p /app/data

# Устанавливаем переменные окружения по умолчанию
ENV DATABASE_PATH=/app/data/database.db
ENV PYTHONUNBUFFERED=1

# Запускаем бота
CMD ["python", "main.py"]
