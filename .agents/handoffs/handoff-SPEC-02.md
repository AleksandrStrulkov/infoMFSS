# Handoff: SPEC-02 — Регистрация по одноразовым приглашениям

## 1. Метаданные
- Дата/время: 2026-11-20 17:54 (UTC+3)
- Ветка: `fix/vps-deploy-and-activation`
- Базовый commit SHA: `783ea5ac42ae6434bdeafb163090e9ea56b19dcc`
- Спецификация: `.agents/specs/SPEC-02-invite-registration.md`

## 2. Что сделано
- Добавлены Invitation, миграция, сервис выпуска с лимитом пяти активных ссылок и атомарного погашения на PostgreSQL.
- Корень закрыт для анонимных посетителей; `users:login` теперь указывает на `/login/`. Старый GET `/users/` безопасно перенаправляет на `/login/` с допустимым `next`, POST `/users/` сохраняет вход прежних клиентов. Убраны открытая регистрация и email-активационный маршрут; восстановление пароля оставлено.
- В профиле добавлены выпуск инвайтов, активные ссылки и история регистраций; регистрация по токену создаёт активного пользователя и авторизует его.
- Добавлены изолированные тесты сценариев, включая параллельные запросы с PostgreSQL; тест старой активации обновлён.
- REWORK по четырём Must Fix: настроен `SECURE_PROXY_SSL_HEADER` при подтверждённом `X-Forwarded-Proto: https` в nginx; профиль выдаёт HTTPS-инвайт за прокси. Защитные заголовки регистрационной формы выставляются единообразно также при конкурентной ошибке POST. Исправлен канонический namespace и безопасная совместимость `/users/`; устаревший шаблон ошибки активации ведёт на запрос доступа, а не на регистрацию без токена.

## 3. Затронутые файлы
- Добавлено: `tests/tests_deploy/test_invite_registration.py`, `users/templates/users/registration_invalid.html`.
- Изменено: `config/settings.py`, `config/urls.py`, `infoMFSS/views.py`, `tests/test_models.py`, `users/forms.py`, `users/models.py`, `users/services.py`, `users/signals.py`, `users/templates/users/activation_failed.html`, `users/templates/users/login.html`, `users/templates/users/register.html`, `users/templates/users/user_form.html`, `users/urls.py`, `users/views.py`.
- Миграции: `users/migrations/0012_invitation.py` (создана; **на рабочей БД не применена**).
- Изменения `.agents/AGENTS.md`, `.agents/agents/techlead.md`, `.agents/verdicts/` принадлежат другим задачам и не тронуты.

## 4. Пакет доказательств (Quality Gate)
Команда: `poetry run gate` — **FAILED** на уже существующих многочисленных ошибках Ruff в файлах вне SPEC-02; общий gate до pytest не дошёл. В контейнере Poetry, Ruff и basedpyright не установлены.
- Ruff: PASSED на `users/services.py`, `users/views.py`, `users/urls.py`, `tests/tests_deploy/test_invite_registration.py` и других перечисленных новых файлах; FAILED при полном прогоне (легаси, в том числе `infoMFSS/admin_import.py`). Затронутые `config/urls.py`, `users/forms.py`, `infoMFSS/views.py` требуют полного переформатирования по Ruff, но это увеличило бы diff в существующем коде.
- basedpyright: FAILED (59 ошибок в проверенной подборке: в том числе текущие определения полей Django без stubs и тестовый Client); 0 ошибок не достигнуто.
- pytest после REWORK: `docker compose exec -T web python -m pytest -q -o addopts= tests/tests_deploy/test_invite_registration.py` — **14 passed**, один warning очистки тестовой PostgreSQL БД (остались открытые соединения). Совместный прогон с `test_power_circuit.py` — **28 passed**, аналогичный warning. `-o addopts=` отключает глобальный порог покрытия только для изолированного прогона; дефолтный pytest без этого аргумента завершался ошибкой coverage (31% < 70%). Ранее полный `tests` — **3 failed, 1 error, 31 passed**: существующие несовпадения фабрики Equipment и проверок `__str__` в `tests/test_forms.py`, `tests/test_models.py`; после REWORK полный набор не запускался.
- Coverage: не подтверждено (при узком прогоне покрытие всего `infoMFSS` ниже порога 70%). Полный gate не завершился: `Exit code: 0` **не получен**.
- Дополнительно: `docker compose exec -T web python manage.py check` после REWORK — без замечаний; ранее `makemigrations --check --dry-run users` — изменений нет; `py_compile` изменённых модулей — успешно.

## 5. Доработка по вердикту REWORK (2026-11-20)
- В `docker-compose.yml` удалена публикация `web:8001:8000`; `web` и `nginx` остаются в общей внутренней сети, nginx обращается к `web:8000`. Локальный `docker compose config --format json` показывает `web ports: []` и общую сеть `infoMFSS-networks`. **Работающий контейнер не пересоздавался**: локальный `docker compose ps` по-прежнему показывает старую публикацию `0.0.0.0:8001->8000/tcp` и `[::]:8001->8000/tcp`. Это подтверждение конфигурации файла, а не закрытия действующего порта или проверки боевого сервера.
- Ruff применён к Python-файлам скоупа: `config/settings.py`, `config/urls.py`, `infoMFSS/views.py`, `tests/test_models.py`, `tests/tests_deploy/test_invite_registration.py`, `users/forms.py`, `users/models.py`, `users/services.py`, `users/signals.py`, `users/urls.py`, `users/views.py`, `users/migrations/0012_invitation.py`. После `poetry run ruff check --fix` и `poetry run ruff format` итоговые `poetry run ruff check <все 12 файлов>` — **All checks passed!**, `poetry run ruff format --check <все 12 файлов>` — **12 files already formatted**. В `users/models.py` порядок `Meta` существующей модели приведён к правилу DJ012. Форматирование затронуло и существующие фрагменты этих файлов; файлы вне скоупа не форматировались.
- Повторный `docker compose exec -T web python -m pytest -q -o addopts= tests/tests_deploy/test_invite_registration.py` после форматирования: **14 passed, 1 warning** (при удалении тестовой PostgreSQL БД осталось одно соединение). Изолированный прогон отключает глобальный порог покрытия через `-o addopts=`.
- Повторный `poetry run gate` завершился **Exit code: 1** на полном Ruff по файлам вне скоупа (в частности, `infoMFSS/admin.py` и `infoMFSS/admin_import.py`); до basedpyright и pytest этот прогон не дошёл. Полный pytest и подтверждение покрытия ≥70% в рамках этой доработки не запускались. Нельзя утверждать полный gate PASS или доказанную изоляцию всех ошибок легаси.
- Перед повторным вердиктом необходимы проверка эффективной конфигурации Compose с overrides и закрытия порта после пересоздания контейнера на целевом сервере, независимая проверка оставшихся gate-ошибок по базовому commit, а также отдельное разрешение на миграцию рабочей БД. Передано на повторное подтверждение ревьюеру и Техлиду; до их решения слияние и боевой деплой заблокированы.

## 6. Известные ограничения / Вопросы
- `docker compose exec -T web python manage.py migrate` не запускалась: инструмент запретил изменение схемы общей рабочей БД без явного разрешения пользователя. Тестовая БД создаётся из миграций автоматически. Применение миграции на рабочей БД требует отдельного разрешения.
- Контракт после REWORK: `reverse('users:login') → /login/`, анонимный `/ → /login/?next=/`; `/users/` сохраняет только совместимый GET-редирект с проверенным `next` и прямой POST-вход без редиректа с паролем. Проверены безопасный/враждебный `next`, HTTPS-ссылка за прокси и заголовки успешного и конфликтного POST. Конфигурация доверенного proxy-заголовка предполагает, что Django доступен только через прокси, который перезаписывает `X-Forwarded-Proto`; публикация порта удалена из файла Compose, но для фактического закрытия прямого доступа необходимо пересоздать контейнер на целевом сервере и проверить сеть/overrides.
- Полный gate и базовые тесты не зелёные; задача **не готова к приёмке READY**. Нужны согласование объёма исправления легаси, повторное прохождение gate и независимое ревью. Не утверждать отсутствие регрессий вне проверенных 25 тестов.
