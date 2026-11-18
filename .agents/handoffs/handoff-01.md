# Handoff: SPEC-01 — Страница схем электроснабжения 127 В

## 1. Метаданные
- Дата/время: 2026-11-18 23:39
- Ветка: develop
- Базовый commit SHA: f587286f815af415758b44568b1b28ffe8505158
- Спецификация: specs/SPEC-01-power-circuit.md

## 2. Что сделано
- Добавлены защищённая страница `/power-circuit/`, каталог схем и двухсегментный эндпоинт JSON. Для JSON и редиректов установлен `Cache-Control: private, no-store`.
- Чтение схем использует только `settings.POWERCIRCUITSCHEMASDIR`: проверяются имена, принадлежность пути корню, ссылки, размер 2 МБ и JSON-объект. Повреждённые файлы исключаются из каталога.
- Карточка главной страницы ведёт на именованный маршрут. React загружает каталог и схему через Django; удалены импорт JSON в бандл и публичный dev-upload.
- Vite собирает движок в `static/power-circuit/` с постоянными именами entry/CSS и chunks. Dockerfile включает код и исходные схемы только в backend-образ; Nginx получает лишь собранную статику. Обновлён AGENTS.md с порядком развёртывания.
- Исправлен преждевременный выход `scripts/gate.py` после первого успешного шага: теперь последующие арбитры действительно запускаются.

## 3. Затронутые файлы
- Добавлено: `infoMFSS/power_circuit.py`, `infoMFSS/power_circuit_views.py`, `infoMFSS/templates/infoMFSS/power_circuit.html`, `tests/tests_deploy/test_power_circuit.py`, `frontend/scripts/smoke_power_circuit.mjs`, `static/power-circuit/` (публичные JS/CSS), `reviews/handoff-01.md`.
- Изменено: `config/settings.py`, `infoMFSS/urls.py`, `infoMFSS/templates/infoMFSS/home.html`, `frontend/src/App.jsx`, `frontend/vite.config.js`, `frontend/package.json`, `Dockerfile`, `.dockerignore`, `AGENTS.md`, `scripts/gate.py`.
- Миграции: нет.
- Предсуществовавшие изменения пользователя в `home.html`, `pyproject.toml` и `poetry.lock` сохранены.

## 4. Пакет доказательств (Quality Gate)
Команда: `poetry run gate`
- Общий итог: **FAILED, exit code 1**; до полного прохождения задача не считается сданной.
- Ruff: **FAILED** на существующих ошибках вне новых модулей (общая статистика: 37 E501, 21 DJ012, 21 F401, 18 W293, 13 I001 и другие). На изменённых Python-файлах Ruff check и format --check — PASSED.
- basedpyright: **0 errors** на изменённых Django-модулях; полный запуск — FAILED на существующих ошибках в `admin.py`, `admin_import.py`, `forms.py` и других файлах.
- pytest: новые защищённые эндпоинты **14 passed, 0 failed** (`docker compose exec -T web python -m pytest tests/tests_deploy/test_power_circuit.py -q -o addopts=''`). Полный набор: **20 passed, 4 failed, 1 error** в существующих тестах форм, моделей и активации.
- Coverage: **91%** для новых сервиса и views при целевом покрытии; общий порог 70% для всего `infoMFSS` не подтверждён.
- Frontend: `npm --prefix frontend run build` и `npm --prefix frontend run smoke` — PASSED: 59 публичных JS/CSS файлов без исходных JSON и названий схем. Django `collectstatic` прошёл; Nginx отдал JS/CSS с HTTP 200, запрос JSON в `/static/` дал 404. Синтаксис Python и `manage.py check` — PASSED. Конвертация существующей схемы в Mermaid проверена для TD и LR; интерактивная проверка браузером и экспортов не проводилась.

## 5. Повторная передача после ревью (2026-11-19)
- **Must Fix 1 — устранено:** `POWERCIRCUITSCHEMASDIR` теперь вычисляется после загрузки `.env`, включая резервный вызов `load_dotenv()`.
- **Must Fix 2 — устранено:** при выборе шахты/схемы синхронно сбрасываются загруженные данные и SVG, устанавливается `loading`; данные привязаны к идентификатору файла, а устаревшие ответы игнорируются по номеру запроса. Экспорт и рендер не используют прежнюю схему под новым именем.
- Проверки: `npm --prefix frontend run build` и `npm --prefix frontend run smoke` — **PASSED** (59 публичных JS/CSS файлов без исходных JSON); Ruff check/format для `config/settings.py` — **PASSED**. `poetry run gate` — **FAILED, exit code 1** на существующих ошибках Ruff в несвязанных файлах (первая ошибка: `infoMFSS/admin.py:1`, I001); остальные шаги гейта этим запуском не выполнены.
- Замечания **Should Fix** не изменялись; оставить в бэклоге.

## 6. Повторная передача: устранение гонки при смене ориентации (2026-11-19)
- Замечание из `.agents/reviews/review-01.md` устранено: переключатель TD/LR сразу сбрасывает `lastSvgRef`. Результат Mermaid теперь хранится вместе с ключом `id схемы + ориентация`; SVG выводится и экспортируется лишь при совпадении ключа с текущим выбором. До окончания рендера экспорт SVG/PNG/PDF не выдаёт прежнюю ориентацию (показывает ожидание); JSON остаётся доступен после загрузки данных. Отменённый рендер не обновляет результат.
- Повторно выполнены `npm --prefix frontend run build` и `npm --prefix frontend run smoke`: **PASSED**, 59 публичных JS/CSS файлов без исходных JSON. Smoke проверяет сборку и приватность файлов, но не имитирует клики и асинхронный Mermaid в браузере.
- Повторный `poetry run gate`: **FAILED, exit code 1** на предсуществующих ошибках Ruff вне изменённого фронтенда (первая — `infoMFSS/admin.py:1`, I001); последующие арбитры не запускались. Не считать гейт зелёным.

## 7. Известные ограничения / Вопросы
- Требуемый `poetry run gate` **не вернул 0** из-за существующего технического долга и падающих тестов вне SPEC-01. Не подавлять ошибки и не менять несвязанные тесты без отдельного решения об объёме работ.
- Полный UI-сценарий в браузере (переключение шахты/схемы, масштаб, экспорт SVG/PNG/PDF/JSON, истечение сессии) пока не подтверждён интерактивным тестом.
- `npm run build` должен быть выполнен до сборки Docker-образа/`collectstatic`; если схемы монтируются отдельным volume вместо копирования, монтировать их только в web, а не в Nginx.
