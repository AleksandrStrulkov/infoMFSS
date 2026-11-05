# Инструкция по деплою

## Настройка базы данных для разных окружений

### Локальная разработка (Windows)

1. **Использование SQLite (рекомендуется для разработки):**
   ```env
   USE_SQLITE=true
   ```
   - Не требует запуска PostgreSQL
   - Быстро и удобно для разработки
   - Миграции создаются и применяются без проблем

2. **Использование PostgreSQL локально:**
   ```env
   USE_SQLITE=false
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5433
   POSTGRES_DB=infomfss
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=ваш_пароль
   ```
   - Требует запущенный PostgreSQL на порту 5433
   - Если возникают проблемы с кодировкой, используйте SQLite

### Docker (локальная разработка с Docker)

В `docker-compose.yml` уже настроено:
- `POSTGRES_HOST=db` (имя сервиса)
- `POSTGRES_PORT=5432` (внутренний порт контейнера)

**Важно:** 
- ❌ Не устанавливайте `USE_SQLITE=true` при работе в Docker!
- ✅ Все команды Django нужно запускать **внутри контейнера** через `docker-compose exec`

Файл `.env` должен содержать:
```env
POSTGRES_DB=infomfss
POSTGRES_USER=postgres
POSTGRES_PASSWORD=ваш_пароль
# POSTGRES_HOST=db устанавливается автоматически через docker-compose.yml
# POSTGRES_PORT=5432 устанавливается автоматически
```

**Правильные команды для работы в Docker:**

```bash
# Создание миграций (если запускаете локально на Windows с проблемами кодировки)
# Локально: poetry run python manage.py makemigrations (с USE_SQLITE=true)

# Применение миграций (ВСЕГДА внутри контейнера!)
docker-compose exec web python manage.py migrate

# Проверка подключения к БД
docker-compose exec web python manage.py check --database default

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Сбор статики
docker-compose exec web python manage.py collectstatic --noinput
```

**Почему команды нужно запускать внутри контейнера:**
- В Docker окружении (Linux) нет проблем с кодировкой psycopg2
- PostgreSQL доступен по имени сервиса `db`
- Все переменные окружения правильно настроены

### Production (сервер)

1. **Создайте `.env` файл на сервере:**
   ```env
   SECRET_KEY=ваш_секретный_ключ
   POSTGRES_DB=infomfss
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=надежный_пароль_только_ASCII
   POSTGRES_HOST=db  # Или IP адрес сервера БД
   POSTGRES_PORT=5432
   DEBUG=False
   ALLOWED_HOSTS=ваш_домен.ru,IP_адрес
   ```

2. **Важно для production:**
   - ❌ **НЕ устанавливайте** `USE_SQLITE=true` в production
   - ✅ Используйте только PostgreSQL
   - ✅ Пароль должен содержать только ASCII символы (латинские буквы, цифры, стандартные символы)
   - ✅ Убедитесь, что файл `.env` сохранен в кодировке UTF-8

3. **Запуск в Docker:**
   ```bash
   docker-compose up -d
   ```

4. **Применение миграций:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Сбор статики:**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

## Автоматическое определение окружения

Система автоматически определяет окружение:

- **Docker окружение:** определяется по наличию `POSTGRES_HOST=db` или файла `/.dockerenv`
  - Всегда использует PostgreSQL
  - Игнорирует `USE_SQLITE=true`

- **Локальное окружение:** определяется автоматически
  - Может использовать SQLite (если `USE_SQLITE=true`)
  - Или PostgreSQL (если параметры заданы и `USE_SQLITE=false`)

## Проверка подключения к БД

Перед деплоем проверьте подключение:

```bash
# В Docker
docker-compose exec web python manage.py check --database default

# Локально
poetry run python manage.py check --database default
```

## Миграции при деплое

### Важно: Разделение локальной разработки и Docker

**Проблема:** На Windows при локальном запуске через `poetry` может возникать ошибка кодировки с psycopg2. Это проблема Windows, а не вашего кода.

**Решение:** Разделить процесс:

1. **Создание миграций (локально на Windows):**
   ```bash
   # Установите USE_SQLITE=true в .env
   poetry run python manage.py makemigrations
   ```
   - Используйте SQLite для создания миграций локально
   - Это избегает проблем с кодировкой на Windows

2. **Применение миграций (ВСЕГДА в Docker!):**
   ```bash
   docker-compose exec web python manage.py migrate
   ```
   - В Docker все работает нормально, проблем с кодировкой нет
   - PostgreSQL доступен и работает корректно

3. **Проверка миграций:**
   ```bash
   docker-compose exec web python manage.py showmigrations
   docker-compose exec web python manage.py migrate --plan
   ```

## Резервное копирование БД

Перед деплоем создайте резервную копию:

```bash
# PostgreSQL
docker-compose exec db pg_dump -U postgres infomfss > backup.sql

# Восстановление
docker-compose exec -T db psql -U postgres infomfss < backup.sql
```

## Чеклист перед деплоем

- [ ] Файл `.env` создан и содержит все необходимые переменные
- [ ] `USE_SQLITE` не установлен в `true` (или отсутствует)
- [ ] `POSTGRES_PASSWORD` содержит только ASCII символы
- [ ] `DEBUG=False` в production
- [ ] `ALLOWED_HOSTS` содержит правильные домены/IP
- [ ] `SECRET_KEY` установлен и безопасен
- [ ] Миграции применены
- [ ] Статика собрана (`collectstatic`)
- [ ] Резервная копия БД создана
