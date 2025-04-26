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
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем код приложения
COPY . .

# Назначаем права
RUN chown -R info-mfss:info-mfss /app

# Переключаем пользователя
USER info-mfss

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]