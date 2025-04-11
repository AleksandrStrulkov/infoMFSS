#!/bin/sh

set -e

echo "⏳ Ожидание базы данных..."
python manage.py wait_for_db

echo "✅ База данных доступна"

echo "⚙️ Миграции..."
python manage.py migrate

echo "⚙️ Компиляция SCSS..."
python manage.py compilescss

echo "📦 Сборка статики..."
python manage.py collectstatic --noinput

echo "👤 Создание суперпользователя..."
python manage.py create_users

echo "🚀 Запуск uWSGI..."
exec uwsgi --ini uwsgi.ini