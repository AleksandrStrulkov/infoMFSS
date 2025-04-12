FROM python:3.12.7-slim

# Проверка и создание пользователя только при необходимости
RUN getent group www-data || addgroup --system www-data && \
    id -u www-data || adduser --system --ingroup www-data www-data

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpcre3-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем код приложения
COPY . .

# Назначаем права
RUN chown -R www-data:www-data /app

# Переключаем пользователя
USER www-data

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]