При старте любой новой сессии первым делом прочитай этот файл для восстановления контекста перед выполнением задач.

# info-mfss — контекст проекта

## Назначение и стек
- Информационный ресурс о внедрении многофункциональной системы безопасности (МФСБ) на нефтешахтах НШПП «Яреганефть»: учет шахт, выработок, оборудования, кабельных трасс, выполнения работ, нарушений и отчетных процентов. Веб-интерфейс преимущественно серверный (Django templates); инженерные схемы — отдельное приложение в `frontend/`.
- Backend: Python 3.12.7 в Docker, Django 5.1.2 (`requirements.txt`), PostgreSQL 15 Alpine, uWSGI 2.0.23, Nginx, Bootstrap, SCSS через `django-sass-processor`, crispy-bootstrap5, django-filter, captcha, openpyxl для импорта Excel. `pyproject.toml`/`poetry.lock` и `uv.lock` также присутствуют; Docker устанавливает **только** `requirements.txt` (списки зависимостей различаются: DRF указан в Poetry, но не в Docker requirements).
- Celery и брокер Redis в compose отсутствуют. В `config/settings.py` есть лишь опциональная настройка Django Redis cache при `CACHE_ENABLED=1`; сервис Redis в compose не определен. Не предполагать наличие фоновых задач или работающего Redis по умолчанию.

## Карта репозитория и приложений
- `config/`: настройки окружения, БД, auth, статики, почты, логирования; корневые URL, WSGI/ASGI. `manage.py` — точка входа команд Django.
- `infoMFSS/`: основная предметная область (`models.py`), формы (`forms.py`), CBV (`views.py`), GET-фильтры (`params.py`) и запросы/проценты (`services.py`); админка и Excel-импорт (`admin.py`, `admin_mixins.py`, `admin_import.py`, `admin_import_utils.py`), шаблоны `templates/infoMFSS/`, миграции и команды `wait_for_db`, `initial_filling_bd`. См. также `ПОРЯДОК_ЗАПОЛНЕНИЯ_МОДЕЛЕЙ.md`; старый `АНАЛИЗ_СТРУКТУРЫ_МОДЕЛЕЙ.md` содержит уже исправленные замечания, сверять с актуальным кодом.
- `users/`: кастомный пользователь, список допущенных лиц, регистрация и email-активация, вход, восстановление пароля, SMS-код/шлюз (`models.py`, `forms.py`, `views.py`, `signals.py`, `sms_utils.py`), команда `create_users`; шаблоны `templates/users/`.
- `static/`: исходные Bootstrap, SCSS/CSS, JS и изображения; `static_collected/` — результат `collectstatic`, а не исходник. `media/` — загружаемые документы. `tests/` и `infoMFSS/tests.py`, `users/tests.py` — тесты; `pytest.ini` задает Django settings и покрытие `infoMFSS`.
- Корневые маршруты `config/urls.py`: `/admin/`, `/chaining/` (smart-selects), `/captcha/`, `/users/`, а `infoMFSS.urls` подключен от `/` с namespace `mfss`. `infoMFSS/urls.py` содержит главную, отчеты/списки, контакт, CRUD `/moderator/...` и временный `/percents_manual/`; `users/urls.py` — вход, регистрация/активация, профиль и сброс пароля. В шаблонах и коде использовать именованные маршруты; при добавлении проверять фактические namespace (`mfss`), не полагаться на старые строковые ссылки.

## Данные и предметные связи
- Топология объекта в БД: `NumberMine` (шахта) → `InclinedBlocks` (уклонный блок) и `Tunnel` (выработка; шахта обязательна, блок опционален); `Surface` — поверхность конкретной шахты. Место установки `EquipmentInstallation` ссылается на тип оборудования `Equipment`, шахту/выработку/блок, опционально `PointPhone` или `BranchesBox`; последние хранят атрибуты точек телефонии/распределительных коробок. `Subsystem` и `Unit` — справочники.
- `Equipment`/`Cable` — каталоги типов и документов. `CableMagazine` — позиция кабельного журнала: тип кабеля, подсистема, шахта, расстояние/единица и опциональные концы `track_from`/`track_to` на `EquipmentInstallation`. Это представление трассы в БД, не JSON-схема фронтенда.
- `EquipmentInstallation.save()` копирует имя, шахту, выработку, пикет и другие поля из связанной телефонной точки/коробки; для телефонной точки пытается установить подсистему с названием `АТС`. `CableMagazine.save()` формирует `name` из концов трассы, отсутствующие заменяет `?`. `Tunnel` и `BranchesBox` также генерируют `name_slag` при сохранении. При импорте/изменении связей учитывать эту логику; `bulk_update`/`queryset.update()` обходят `save()`.
- `Execution` хранит факт и даты выполнения для установки оборудования **или** позиции кабельного журнала. Его `save()` обновляет обратную ссылку `EquipmentInstallation.equipment_bool`; `CableMagazine.cable_bool` — отдельная nullable-ссылка на `Execution`. `PercentService` считает долю `execution_bool=True` среди записей `Execution` по шахте/подсистеме/блоку; сервисы в `services.py` фильтруют списки и считают количество/длину. `BaseFilterService` возвращает пустой queryset до передачи GET-параметров (`FilterParams`). В формах используются справочные записи «Все шахты», «Все подсистемы», «Все уклонные блоки» и т. п. — это реальные объекты, не только UI-значения.
- `Beacon` — маячки с шахтой, выработкой/блоком, MAC, серийным номером, minor и датой монтажа; поле `subsystem` здесь строковое, не FK. `Violations` — нарушения и акты; `Visual` — PDF-визуализации с привязками к шахте/оборудованию/кабелю; `DateUpdate` — дата обновления. `DailyNumbersMine`, `ManualPercentage`, `Surface` и `PercentManualService` помечены в коде как временное решение до заполнения БД; главная страница предпочитает последний `DailyNumbersMine`, при отсутствии берет вычисленные проценты.
- `users.User` наследует `AbstractUser`, не имеет `username`, использует уникальный email как `USERNAME_FIELD`; `AllowedPerson` ограничивает регистрацию по ФИО, `SMSDevice` хранит коды. Регистрация создает неактивного пользователя и отправляет ссылку активации по email. **Фактически SMS-проверка при входе сейчас закомментирована** в `users/views.py`: после пароля вызывается `login()` напрямую, хотя SMS-маршрут/модель и README описывают двухфакторный сценарий.

## Отдельный frontend инженерных схем
- `frontend/` — React 18 + Vite 5 + Mermaid 11 интерфейс инженерных схем. Для публикации движка: из `frontend/` выполнить `npm ci && npm run build`, затем Django `collectstatic`; собранные JS/CSS попадают в `static/power-circuit/`, а закрытые JSON остаются в `frontend/src/data/schemas/` и выдаются только авторизованным пользователям Django. Node не требуется для обслуживания страницы. Для разработки `npm run dev` запускает Vite на порту **5173**.
- JSON-файлы `frontend/src/data/schemas/mine_N/*.json` выбираются через `import.meta.glob`; `mine` задает подпись шахты, `locations` — группы устройств, ключи `connections_*` — массивы связей `{from, to, cable?}`, `to` может быть строкой или массивом. `jsonToMermaid.js` валидирует и превращает схему в Mermaid; `postProcessDiagram.js` исправляет SVG-геометрию узлов, подписей и кабелей; `exportDiagram.js` экспортирует SVG/PNG/PDF/JSON. `App.jsx` управляет выбором шахты/схемы, ориентацией TD/LR, темой и масштабом.
- Каталог и JSON-схемы выдаются только через защищённые Django GET-маршруты `/power-circuit/schemas/` и `/power-circuit/schemas/<mine_dir>/<filename>/`; upload через браузер отсутствует. Настройка `POWERCIRCUITSCHEMASDIR` задаёт корень закрытых схем (абсолютный путь или относительно `BASE_DIR`), по умолчанию `frontend/src/data/schemas/`. Backend-образ содержит исходные схемы; вместо копирования при развёртывании допускается отдельный volume только в web, без доступа Nginx. Изменение JSON не требует пересборки Vite или collectstatic. `frontend/scripts/postprocess_check.mjs` проверяет рендер схем; `cluster_check.mjs` ссылается на старый путь к JSON — перед использованием сверить путь. Не смешивать JSON-топологию фронтенда с ORM-моделями без явно спроектированной синхронизации.

## Инфраструктура, запуск и ограничения
- Создать `.env` по `.env.sample` (секреты не коммитить). `docker compose build && docker compose up -d`; статус/логи: `docker compose ps`, `docker compose logs -f web`. `db` проверяется healthcheck, затем `web` запускает `entrypoint.sh`: `wait_for_db` → `migrate` → `compilescss` → `collectstatic --noinput` → `create_users` → `initial_filling_bd` → uWSGI. Заполнение выполняется **при каждом старте**; команда перехватывает исключения и печатает ошибку, поэтому проверять ее вывод. Для изменений модели: `docker compose exec web python manage.py makemigrations`, затем `docker compose exec web python manage.py migrate`; тесты: `docker compose exec web pytest` (либо локально при подготовленных зависимостях).
- `web`: хост `localhost:8001` → контейнер `8000`; PostgreSQL: хост `localhost:5433` → контейнер `5432`; в сети Compose обращаться к БД по `db:5432`. Перед сборкой backend-образа выполнить `npm ci && npm run build` внутри `frontend/`, затем `docker compose build` — Dockerfile копирует готовый движок и закрытые исходные JSON; не монтировать каталог схем в Nginx и не добавлять его в публичную статику. `nginx` опубликован на `80` и `443`, но предоставленный `nginx/nginx.conf` содержит только HTTP server на `80` (TLS listener отсутствует). Nginx проксирует `web:8000` и отдает `/static/`, `/media/` из общих каталогов.
- Том `postgres_data` постоянный; `web` bind-монтирует **весь корень** в `/app` и отдельно `static_collected/`, `media/`, `logs/`; Nginx читает последние два. Поэтому изменение файлов на хосте видно в контейнере, но uWSGI не обязан автоматически перезапускаться; пересборка образа не заменяет файлы в bind mount. В `entrypoint.sh` есть `chown/chmod` для Windows bind mounts, затем сервер работает под `info-mfss`; `uwsgi.ini` настроен на 4 процесса × 2 потока.
- `config/settings.py` выбирает SQLite локально при `USE_SQLITE=true` **или** отсутствии полных PostgreSQL credentials; в Docker принудительно PostgreSQL. Локальный порт БД по умолчанию 5433, но пустой/иной `POSTGRES_PORT` из `.env` переопределяет его. Статика компилируется из `static/` в `static_collected/`; файлы загрузок — `media/`. Для работы логирования должен существовать каталог `logs/` (файл `logs/infoMFSS.log` создается обработчиком). В `README.md` и `DEPLOY.md` есть дополнительные инструкции, но фактическую конфигурацию сверять с кодом.
- Настройки `DEBUG` (или `DJANGO_DEBUG`) и дополнительные `ALLOWED_HOSTS` берутся из `.env`; `ALLOWED_HOSTS` задаёт имена/IP без схемы и порта, `CSRF_TRUSTED_ORIGINS` — полные origin со схемой и портом при необходимости, оба списка через запятую. `CORS_ALLOWED_ORIGINS` объявлен, но `corsheaders` не включен в `INSTALLED_APPS`/`MIDDLEWARE`. Не считать данный compose production-ready без отдельной проверки настроек безопасности и TLS.

## Соглашения для изменений
- Использовать имеющееся разделение: модель и инварианты в `models.py`, проверка/ввод в `forms.py`, SQL-фильтрация и агрегаты в `services.py`, HTTP и контекст шаблона в CBV `views.py`; маршрут с именем — в соответствующем `urls.py`, шаблон — в `templates/<app>/`, статика — в `static/`. Для новых CRUD-операций соблюдать `LoginRequiredMixin` и `PermissionRequiredMixin` с точным Django permission (`add_`, `change_`, `delete_`); не считать префикс `/moderator/` сам по себе защитой. Списковые views редактирования сейчас местами ограничены только `LoginRequiredMixin` — проверять доступ к каждому новому маршруту отдельно.
- Для новой сущности/связи: оценить порядок заполнения и nullable/cascade, добавить миграцию, обновить админку/формы/фильтры/шаблоны и тесты. Использовать существующие namespace `mfss`/`users` и `reverse_lazy`; при работе с процентами помнить реальные записи «Все …» и временные ручные данные. Excel-импорт реализован в админке отдельно от обычных форм.
- Python: Black `line-length = 119` (`pyproject.toml`), Flake8 `max-line-length = 119`, `ignore = E203,W503` (`.flake8`); Poetry задает Black/isort/Flake8 в группе lint, Docker их не устанавливает через `requirements.txt`. Тесты `pytest`/`pytest-django`/factory-boy, настройка в `pytest.ini`. Для фронтенда править генератор/постпроцессор отдельно от данных JSON и проверять обе ориентации, экспорт и SVG-скрипты; отсутствует отдельный `npm test` в `package.json`.

## Автоматическая маршрутизация скиллов (Skills Routing Engine)

Ты обязан активировать и строго исполнять регламенты из директории `.agents/skills/` в зависимости от входящей задачи:

| Тип задачи / Триггер | Обязательный скилл | Действие агента |
|:--- |:--- |:--- |
| Создание или изменение Python-файлов, сервисов, вьюх, моделей | `.agents/skills/clean-code-standards/SKILL.md` | Применять строгую типизацию (PEP 484/585/604), принципы SOLID, выносить бизнес-логику из views в services. |
| Реализация новой фичи, эндпоинта или крупный рефакторинг | `.agents/skills/feature-workflow/SKILL.md` | Сначала прочитать связанные файлы, составить контракт изменений, внести правки, проверить компиляцию. |
| Написание, запуск, отладка или перенос тестов | `.agents/skills/test-pipeline/SKILL.md` | Черновики и быстрые проверки — в `tests/test_temporary/`, стабильные тесты — в `tests/tests_deploy/`. Запуск строго через Docker. |
| Выполнение команд Django (миграции, статика, шелл) или управление сервисами | `.agents/skills/docker-runner/SKILL.md` | Выполнять команды исключительно через `docker compose exec web...`. Никаких локальных запусков вне контейнера. |
| Ошибки, 500-е коды, падения тестов или трейсбеки | `.agents/skills/debug-investigate/SKILL.md` | Снять логи контейнера, локализовать причину в коде, выдвинуть гипотезу перед правкой. |

### Правила автономного исполнения:
1. Запрещено писать/модифицировать Python-код без активации `clean-code-standards`.
2. Если задача комплексная (например: «создай эндпоинт схемы 127В и напиши тест»), применяй цепочку скиллов: `feature-workflow` + `clean-code-standards` на этапе кода → `test-pipeline` на этапе проверки.
3. Перед генерацией кода не требуй от пользователя ввода префиксов скиллов — считывай контекст и применяй правила по умолчанию.

## Слой 3 и 4: Гардрайлы, Quality Gates и Eval-петля

Перед завершением любой задачи, связанной с изменением или добавлением кода, ты ОБЯЗАН запустить единый скрипт гейткипера и получить подтверждение прохождения всех машинных арбитров. Никакие субъективные оценки («код выглядит рабочим», «визуально всё ок») не принимаются.

### Обязательный пайплайн верификации (арбитры Слоя 3):
1. **Линтинг и сортировка импортов (Ruff на Rust):**
 - Проверка правил: `poetry run ruff check.`
2. **Форматирование кода (Ruff Format):**
 - Проверка стиля (длина строки 119): `poetry run ruff format --check.`
3. **Статическая типизация (basedpyright):**
 - Контракт типов без неявных `Any`: `poetry run basedpyright`
4. **Тесты и покрытие (Pytest + Coverage):**
 - Прогон тестов без миграций и замер покрытия (порог не ниже 70%): `poetry run pytest`

---

### Запуск через Eval-петлю (Слой 4):

Вместо ручного ввода отдельных команд запускай единый детерминированный гейт:
- **Локально (хост):**
 ```powershell
 poetry run gate
 ```
- **Или внутри Docker (если работаешь в контейнере):**
 ```bash
 docker compose exec web poetry run gate
 ```
- **Для проверки одного конкретного файла:**
 ```powershell
 poetry run gate &lt;путь_к_файлу&gt;
 ```

---

### Правило сдачи работы:
- Задача **НЕ СЧИТАЕТСЯ ВЫПОЛНЕННОЙ**, пока в выводе скрипта гейта не появится подтверждение: `Exit code: 0`.
- При падении любого шага ты обязан самостоятельно прочитать трассировку из `stderr/stdout`, локализовать дефект, внести правки и повторить прогон петли.
- Строго запрещено маскировать дефекты через `# type: ignore`, `# noqa` или `noqa: E501` без явного технического обоснования и согласования.


## Конвейер разработки и роли
## 0. Первое действие любого агента (КРИТИЧНО)
Перед началом любой работы агент ОБЯЗАН прочитать разделы контекста этого файла (`.agents/AGENTS.md`) выше.
Без знания ограничений БД, save()-хуков и изоляции frontend/ к коду не прикасаться.

## 1. Стек и ограничения
- Python 3.12, Django 5.1.2.
- База данных: PostgreSQL 15, веб-сервер: uWSGI + Nginx.
- Пакетный менеджер: Poetry локально, requirements.txt в Docker.
- Фронтенд схем: отдельный React/Vite в `frontend/`, не путать JSON-топологию с моделями Django.
- Шлюз качества: `poetry run gate` (Ruff, basedpyright strict, pytest).

## 2. База знаний и стандарты (читать перед работой)
- Стандарты кода:.agents/agents/python-standards.md
- Регламент ошибок:.agents/agents/error-handling.md
- Логирование:.agents/agents/logging.md
- Правила тестирования:.agents/agents/testing.md
- Правила рефакторинга:.agents/agents/refactor.md

## 3. Конвейер разработки и роли
1. Роли:
 - Планировщик:.agents/agents/planner.md — анализирует требования, проектирует архитектуру, декомпозирует задачу на шаги и формирует готовую спеку в specs/ без написания продакшн-кода.
 - Кодер:.agents/agents/coder.md — пишет код строго по спеке от Планировщика, сдаёт через poetry run gate == 0.
 - Ревьюер:.agents/agents/reviewer.md — проверяет diff, заполняет reviews/review-*.md.
 - Техлид:.agents/agents/techlead.md — финальная приёмка по 5 рубрикам, выносит итоговый вердикт в verdicts/verdict-*.md.

2. Порядок работы (Pipeline):
 - Старт: Планировщик формирует спеку задачи specs/SPEC-XX-*.md (по шаблону specs/task-template.md).
 - Разработка: Кодер реализует задачу по утверждённой спеке.
 - Сдача от Кодера: handoffs/handoff-*.md (по шаблону handoffs/handoff-template.md).
 - Отчёт Ревьюера: reviews/review-*.md (по шаблону reviews/review-template.md).
 - Приёмка Техлидом: формирует verdicts/verdict-*.md (по шаблону verdicts/verdict-template.md) с итоговой резолюцией READY, REWORK или ESCALATE.

## 4. Главный закон
Код считается неготовым, если:
- Нет утверждённой спеки от Планировщика в specs/.
- Упал poetry run gate (код возврата не 0) без явного применения правила изоляции легаси.
- Затронута логика EquipmentInstallation.save() или CableMagazine.save() без учёта хуков.
- Отсутствует или не заполнен handoff-пакет.
- Есть хотя бы одно блокирующее замечание от Ревьюера.
- Отсутствует вердикт Техлида со статусом READY в verdicts/.