#!/bin/sh

set -e

# Устанавливаем права на монтируемые директории (для Windows bind mounts)
echo "🔧 Установка прав доступа на директории..."
chown -R info-mfss:info-mfss /app/static_collected /app/media /app/logs 2>/dev/null || true
chmod -R 755 /app/static_collected /app/media /app/logs 2>/dev/null || true

# Очищаем директорию static_collected перед сборкой (опционально)
# rm -rf /app/static_collected/* 2>/dev/null || true

echo "⏳ Ожидание базы данных..."
python manage.py wait_for_db

echo "✅ База данных доступна"

echo "⚙️ Миграции..."
python manage.py migrate

echo "⚙️ Компиляция SCSS..."
python manage.py compilescss

echo "📦 Сборка статики..."
# Запускаем collectstatic от текущего пользователя (root), затем меняем права
python manage.py collectstatic --noinput
chown -R info-mfss:info-mfss /app/static_collected 2>/dev/null || true

echo "👤 Создание суперпользователя..."
python manage.py create_users

echo "👤 Заполнение БД начальными данными..."
python manage.py initial_filling_bd

# Переключаемся на пользователя info-mfss для запуска uWSGI
echo "🔄 Переключение на пользователя info-mfss..."
exec su -s /bin/sh info-mfss -c "uwsgi --ini uwsgi.ini"