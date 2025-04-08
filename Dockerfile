# ===== Билд-стадия =====
FROM python:3.12-slim as builder

# Устанавливаем только необходимые для сборки зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем и активируем виртуальное окружение
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===== Финальный образ =====
FROM python:3.12-slim

# Устанавливаем только необходимые runtime-зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Копируем виртуальное окружение из builder-стадии
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Создаём непривилегированного пользователя
RUN groupadd -r appuser && \
    useradd -r -s /bin/false -g appuser appuser && \
    mkdir /app && \
    chown appuser:appuser /app

WORKDIR /app

# Копируем код приложения
COPY --chown=appuser:appuser . .

# Настройки окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONPYCACHEPREFIX=/tmp/.pycache \
    DJANGO_SETTINGS_MODULE=config.settings

# Собираем статику
RUN python manage.py collectstatic --noinput --clear

# Переключаемся на непривилегированного пользователя
USER appuser

# Команда запуска
CMD ["gunicorn", "config.wsgi:application", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "4", \
    "--threads", "2", \
    "--worker-class", "gthread", \
    "--timeout", "120", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]
