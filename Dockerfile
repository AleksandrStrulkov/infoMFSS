# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Установка setuptools и обновление pip
RUN pip install --upgrade pip setuptools wheel

## Создаем структуру папок и файлов
#RUN mkdir -p /logs && touch /logs/infoMFSS.log \
#    && chmod 666 /logs/infoMFSS.log  # Делаем файл доступным для записи

# Создаем и переходим в рабочую директорию
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Собираем статику (для production)
RUN python manage.py collectstatic --noinput --clear

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
# Настройки окружения
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

# Команда запуска (для development)
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Для production CMD:
 CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

