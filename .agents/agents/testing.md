# Testing rules (Django / DRF / pytest-django)

- Использовать `pytest` совместно с `pytest-django`.
- Не использовать громоздкие `unittest.TestCase`, классы без необходимости, `setUp` и `tearDown` — писать плоские функции и pytest-фикстуры.
- Во всех тестовых файлах объявлять `from __future__ import annotations`.
- Проект классический синхронный Django: тесты объявляются через `def test_...()` (без async, если явно не тестируются channels/асинхронные воркеры).
- Для тестов, работающих с ORM или базой данных, обязательно указывать метку `@pytest.mark.django_db`.

## Unit tests (сервисы, селекторы, вспомогательные функции)

- Unit-тесты должны быть быстрыми, детерминированными и изолированными.
- Не использовать общее состояние (shared state) между тестами.
- Не тестировать HTTP/REST API на уровне юнит-тестов (для этого есть интеграционный слой).
- Для изоляции чистой логики отдавать предпочтение явным Fake-объектам или передаче DTO/dataclass вместо глубокого моканья Django ORM через `unittest.mock`.
- Если объект не найден, проверять строго `is None`.
- Для проверки ожидаемых исключений использовать `pytest.raises(..., match=...)`.
- Именование тестов понятное и говорящее: `test_<функция>_<условие>_<ожидаемый_результат>`.

### Что проверять в Unit tests:
- Основной позитивный сценарий (Happy path).
- Граничные условия (Edge cases): пустой список оборудования, None в опциональных параметрах, нулевые нагрузки, крайние длины строк.
- Обработку ошибок: валидация входных структур, неверные типы данных.
- Регрессионный тест на каждый обнаруженный и исправленный баг.

## Integration tests (API / DRF ViewSets / эндпоинты)

- Интеграционные тесты проверяют корректность эндпоинтов целиком: от роутинга и парсинга параметров до сериализатора и ответа БД.
- Использовать DRF-клиент `rest_framework.test.APIClient` (или готовую фикстуру `api_client`).
- Очистка базы данных: транзакционная изоляция обеспечивается автоматически через метку `@pytest.mark.django_db` — никаких ручных `DELETE FROM` писать не нужно.
- Проверять точные HTTP-статусы (`status.HTTP_200_OK`, `status.HTTP_400_BAD_REQUEST`, `status.HTTP_404_NOT_FOUND`) и структуру JSON в `response.data` / `response.json()`.
- При тестировании авторизации и прав явно логинить пользователя через `api_client.force_authenticate(user=user)`.

Пример теста эндпоинта:
```python
import pytest
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_get_substation_layout_success(api_client: APIClient, sample_substation):
 response = api_client.get(f"/api/v1/substations/{sample_substation.id}/layout/")
 
 assert response.status_code == status.HTTP_200_OK
 assert response.json()["id"] == sample_substation.id
Покрытие и доказательства качества
Для прогона тестов и проверки покрытия использовать Poetry:
poetry run pytest tests/ --cov=infoMFSS --cov-fail-under=70
Запрещено добиваться нужного процента искусственно:
Никаких фиктивных ассертов вроде assert True.
Запрещено проставлять # pragma: no cover, pytest.mark.skip или xfail без прямого обоснования и разрешения в спеке задачи.
Финальный критерий приёмки тестов: успешный запуск единого шлюза poetry run gate с нулевым кодом возврата (Exit code: 0).