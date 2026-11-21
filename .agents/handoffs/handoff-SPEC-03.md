# Handoff: SPEC-03 — Единый интерфейс профиля и приглашений

## 1. Метаданные
- Дата/время: 2026-11-20 20:14 (UTC+3)
- Ветка: `fix/vps-deploy-and-activation`
- Базовый commit SHA: `5c6b1bdc71d47735a93d24cda3b1140c5394f6a5`
- Спецификация: `.agents/specs/SPEC-03-profile-ui-refactoring.md`

## 2. Что сделано
- Форма профиля и приглашения размещены в общей центральной адаптивной колонке; две карточки имеют одинаковое оформление и стандартный отступ.
- Действующие ссылки оформлены списком с бейджем статуса, датой окончания и полем с кнопкой копирования. История регистраций оформлена списком с бейджем «Использован».
- Сохранены раздельные POST-формы, CSRF-токены, маршрут генерации приглашений и ссылка смены пароля. Для формы профиля используется `{{ form|crispy }}`, чтобы существующая внешняя форма не получила вложенный тег `<form>`.
- Сообщения выпуска приглашений оформлены стандартными Bootstrap alerts; инлайн-стили не добавлялись.

## 3. Затронутые файлы
- Изменено: `users/forms.py`, `users/views.py`, `users/admin.py`, `users/templates/users/user_form.html`.
- Обновлено: `.agents/handoffs/handoff-SPEC-03.md`.
- Добавлена презентационная `InviteDisplayForm`; ссылка приглашения теперь рендерится через crispy-forms, выпуск вынесен в отдельную POST-форму без вложенности.
- Добавлен `InvitationAdmin`: ссылка, создатель, даты, статус, фильтры, поиск и readonly-токен/ссылка.
- Исправлена регистрация `Invitation`: после создания кастомного `MyAdminSite` импортируется `users.admin`, поэтому модель регистрируется именно в реестре админки `/admin/`.
- В `InvitationAdmin` первым столбцом списка добавлен кликабельный `id`; идентификатор также отображается в карточке объекта как readonly-поле.
- Миграции: нет.

## 4. Пакет доказательств (Quality Gate)
- `git diff --check`: PASSED (Git предупреждает о настройке преобразования LF/CRLF).
- `poetry run python manage.py check`: PASSED, 0 замечаний; предупреждение об отсутствующем openpyxl.
- `docker compose exec -T web python -m pytest -q -o addopts= tests/tests_deploy/test_invite_registration.py`: **14 passed, 1 warning**. Warning касается удаления тестовой PostgreSQL БД при оставшихся соединениях. Порог покрытия этим изолированным запуском отключён.
- `poetry run gate`: **FAILED** на существующих ошибках Ruff вне скоупа SPEC-03 (`infoMFSS/admin.py`, `infoMFSS/admin_import.py` и другие); до следующих стадий gate не дошёл.
- `poetry run ruff check users/admin.py`: **PASSED**.
- `poetry run basedpyright users/admin.py`: **PASSED**.
- `poetry run pytest tests/tests_deploy/test_invite_registration.py`: **FAILED на окружении** — PostgreSQL соединение завершается `UnicodeDecodeError`; также coverage падает из-за неполного запуска (`30% < 70%`).
- Отдельного HTML/JS-линтера не запускалось. Coverage не измерялось.

## 5. Известные ограничения / Вопросы
- Backend выдаёт только активные и использованные приглашения; истёкшие ссылки не передаются в шаблон, поэтому бейдж «Истёк» не отображается. Изменение выборки потребовало бы вмешательства в backend и не входило в эту UI-задачу.
- Автоматические тесты подтверждают сохранность сценариев приглашений, но реальная браузерная проверка адаптивной вёрстки и работы буфера обмена не проводилась.
- На локальной машине тесты напрямую через Poetry не подключаются к PostgreSQL по hostname `db`; проверка выполнялась внутри контейнера. Контейнер `web` не пересоздавался и всё ещё публикует порт 8001 по старой конфигурации (вопрос предыдущей задачи).

## 6. Дополнение от 2026-11-21: CSRF регистрации и страницы ошибок
- Уточнение к исходной проблеме: `{% csrf_token %}` и кнопка уже находились внутри внешнего `<form>`, но `{% crispy form %}` создавал вложенную форму. В `users/templates/users/register.html` оставлен один внешний POST-form и использован `{{ form|crispy }}`.
- Добавлены корневые шаблоны `templates/400.html`, `403.html`, `403_csrf.html`, `404.html`, `500.html`; для 500 применён автономный HTML со статическими CSS без наследования от базового шаблона, его navbar, context processors и запросов к БД. Остальные страницы наследуют `users/base.html` и сохраняют навигацию/Bootstrap.
- Настроен `CSRF_FAILURE_VIEW` в `config/views.py`; причина отклонения запроса пользователю не выводится. Дополнительные `ALLOWED_HOSTS` (без схемы и порта) и `CSRF_TRUSTED_ORIGINS` (полные http/https origin) читаются из `.env`; обновлены `.env.sample` и `.agents/AGENTS.md`.
- Добавлены регрессионные тесты структуры формы, POST с CSRF-проверкой, отображения страниц ошибок и переменных окружения.
- `docker compose exec -T web python manage.py check`: PASSED. `docker compose exec -T web python -m py_compile ...`: PASSED. `poetry run ruff check` изменённых Python-файлов: PASSED. `poetry run ruff format --check` изменённых Python-файлов: PASSED. `poetry run basedpyright config/views.py tests/tests_deploy/test_error_settings.py`: PASSED. `git diff --check`: PASSED.
- `docker compose exec -T web python -m pytest -q -o addopts= tests/tests_deploy/test_invite_registration.py tests/tests_deploy/test_error_settings.py`: **18 passed, 1 warning** (PostgreSQL не смог удалить тестовую БД из-за оставшегося соединения).
- Полный `docker compose exec -T web python -m pytest -q`: **FAILED — 3 failed, 1 error, 39 passed; coverage 33% < 70%**. Существующие тесты `tests/test_forms.py`/`tests/test_models.py` не соответствуют актуальным полям и строковому представлению моделей. `poetry run ruff check .` и `poetry run gate`: **FAILED** на существующих ошибках в `infoMFSS/admin.py`, `infoMFSS/admin_import.py` и др. Локальный `poetry run gate config/views.py` также не проходит из-за подключения PostgreSQL (`UnicodeDecodeError`) и coverage. Полный basedpyright существующего файла `test_invite_registration.py` выдаёт многочисленные ошибки типизации Django/pytest.
- Требуется указать фактический публичный IP/host и его http/https origin в `.env` сервера; конфигурация не может заранее вывести их автоматически. Для применения настроек перезапустить web; браузерный прогон на публичном сервере не выполнялся.
