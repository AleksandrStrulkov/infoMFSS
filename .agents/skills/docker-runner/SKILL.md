---
name: docker-runner
description: Регламент выполнения команд управления приложением, базой данных и зависимостями внутри контейнеров.
argument-hint: "[команда для выполнения, например: migrate, test, check]"
---

Правила выполнения инфраструктурных команд:
1. Контейнерная изоляция: Все команды управления Django (`manage.py`), тесты и скрипты выполняй ИСКЛЮЧИТЕЛЬНО через `docker compose exec web <команда>`. Запрещено выполнять `python manage.py` напрямую на хосте.
2. Миграции базы данных:
 - Создание: `docker compose exec web python manage.py makemigrations`
 - Применение: `docker compose exec web python manage.py migrate`
 - После миграций всегда проверяй статус и вывод на наличие ошибок integrity/foreign key.
3. Системные проверки: Для валидации состояния Django используй `docker compose exec web python manage.py check`.