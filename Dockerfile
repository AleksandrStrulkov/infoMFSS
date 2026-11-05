FROM python:3.12.7-slim

# Проверка и создание пользователя
RUN getent group info-mfss || addgroup --system info-mfss && \
    id -u info-mfss || adduser --system --ingroup info-mfss info-mfss

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

# Устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем только необходимые файлы для сборки
# Остальной код будет смонтирован через volume в docker-compose
COPY entrypoint.sh uwsgi.ini ./
RUN chmod +x ./entrypoint.sh

# Создаем директории для логов и медиа
RUN mkdir -p /app/logs /app/media /app/static_collected

# Не переключаем пользователя здесь - entrypoint.sh будет запускаться от root
# для установки прав на монтируемые директории, затем переключится на info-mfss

ENTRYPOINT ["./entrypoint.sh"]