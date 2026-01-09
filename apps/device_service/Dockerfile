# Многостадийная сборка для оптимизации размера образа
FROM python:3.12-slim AS builder

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка poetry для управления зависимостями
RUN pip install --no-cache-dir poetry==1.8.3

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock* ./

# Установка зависимостей
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# Финальный этап - production образ
FROM python:3.12-slim AS production

# Установка runtime зависимостей (исправлен многострочный RUN)
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для безопасности
RUN addgroup --system app && adduser --system --group app

# Рабочая директория
WORKDIR /app

# Копирование зависимостей из builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копирование исходного кода
COPY app/ ./app/
COPY config.yml .
COPY requirements.txt .

# Права доступа
RUN chown -R app:app /app
USER app

# Переменные окружения
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8082

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Запуск приложения (shell-форма для интерполяции ${PORT})
EXPOSE $PORT
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8082}"