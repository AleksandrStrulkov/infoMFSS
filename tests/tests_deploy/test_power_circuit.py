from __future__ import annotations

import json
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, override_settings
from django.urls import reverse

from infoMFSS.power_circuit import MAX_SCHEMA_BYTES


@pytest.fixture
def authenticated_client(db: object) -> Client:
    user = get_user_model()(email="schemas@example.test")
    user.set_password("test-pass")
    user.save()
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def schema_root(tmp_path: Path) -> Path:
    directory = tmp_path / "mine_1"
    directory.mkdir()
    (directory / "sample.json").write_text(
        json.dumps({"mine": "Шахта 1", "locations": {"point": ["device"]}, "connections_main": []}),
        encoding="utf-8",
    )
    return tmp_path


def test_page_route_and_guest_redirect(client: Client, authenticated_client: Client) -> None:
    url = reverse("mfss:power_circuit")
    assert url == "/power-circuit/"
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f"{reverse('users:login')}?next={url}"
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert b"/src/main.jsx" not in response.content
    assert b"power-circuit/app.js" in response.content
    assert reverse("mfss:power_circuit_schemas").encode() in response.content


def test_guest_cannot_read_schema_endpoints(client: Client) -> None:
    urls = [
        reverse("mfss:power_circuit_schemas"),
        reverse("mfss:power_circuit_schema", kwargs={"mine_dir": "mine_1", "filename": "sample.json"}),
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code == 302
        assert response["Cache-Control"] == "private, no-store"
        assert response.url == f"{reverse('users:login')}?next={url}"


def test_authenticated_catalog_and_schema(authenticated_client: Client, schema_root: Path) -> None:
    with override_settings(POWERCIRCUITSCHEMASDIR=schema_root):
        catalog = authenticated_client.get(reverse("mfss:power_circuit_schemas"))
        assert catalog.status_code == 200
        assert catalog["Cache-Control"] == "private, no-store"
        assert catalog.json() == {"schemas": [{"id": "mine_1/sample.json", "mine": "Шахта 1", "name": "sample"}]}
        schema = authenticated_client.get(
            reverse("mfss:power_circuit_schema", kwargs={"mine_dir": "mine_1", "filename": "sample.json"})
        )
        assert schema.status_code == 200
        assert schema["Cache-Control"] == "private, no-store"
        assert schema.json() == json.loads((schema_root / "mine_1" / "sample.json").read_text(encoding="utf-8"))


def test_default_schema_root(authenticated_client: Client) -> None:
    assert Path(settings.POWERCIRCUITSCHEMASDIR).is_absolute()
    response = authenticated_client.get(reverse("mfss:power_circuit_schemas"))
    assert response.status_code == 200
    assert isinstance(response.json()["schemas"], list)


def test_catalog_excludes_invalid_schemas(authenticated_client: Client, schema_root: Path) -> None:
    directory = schema_root / "mine_1"
    (directory / "broken.json").write_text("{broken", encoding="utf-8")
    (directory / "oversized.json").write_bytes(b"x" * (MAX_SCHEMA_BYTES + 1))
    (directory / "array.json").write_text("[]", encoding="utf-8")
    (schema_root / "mine_0").mkdir()
    (schema_root / "mine_0" / "other.json").write_text("{}", encoding="utf-8")
    with override_settings(POWERCIRCUITSCHEMASDIR=schema_root):
        response = authenticated_client.get(reverse("mfss:power_circuit_schemas"))
    assert [entry["name"] for entry in response.json()["schemas"]] == ["sample"]


@pytest.mark.parametrize(
    ("directory", "filename"),
    [
        ("mine_0", "sample.json"),
        ("mine_1", "missing.json"),
        ("mine_1", "sample.txt"),
        ("..", "sample.json"),
        ("mine_1", "..sample.json"),
        ("mine_1", "nested\\sample.json"),
    ],
)
def test_invalid_schema_returns_404(
    authenticated_client: Client, schema_root: Path, directory: str, filename: str
) -> None:
    with override_settings(POWERCIRCUITSCHEMASDIR=schema_root):
        response = authenticated_client.get(
            reverse("mfss:power_circuit_schema", kwargs={"mine_dir": directory, "filename": filename})
        )
    assert response.status_code == 404
    assert str(schema_root).encode() not in response.content


def test_invalid_json_and_large_file_return_404(authenticated_client: Client, schema_root: Path) -> None:
    directory = schema_root / "mine_1"
    (directory / "broken.json").write_text("{invalid", encoding="utf-8")
    (directory / "large.json").write_bytes(b"x" * (MAX_SCHEMA_BYTES + 1))
    with override_settings(POWERCIRCUITSCHEMASDIR=schema_root):
        for filename in ("broken.json", "large.json"):
            response = authenticated_client.get(
                reverse("mfss:power_circuit_schema", kwargs={"mine_dir": "mine_1", "filename": filename})
            )
            assert response.status_code == 404
            assert str(schema_root).encode() not in response.content


def test_symlinks_do_not_escape_root(authenticated_client: Client, schema_root: Path, tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside_schema_test.json"
    outside.write_text('{"mine":"private"}', encoding="utf-8")
    try:
        (schema_root / "mine_1" / "link.json").symlink_to(outside)
        with override_settings(POWERCIRCUITSCHEMASDIR=schema_root):
            response = authenticated_client.get(reverse("mfss:power_circuit_schemas"))
            assert [entry["name"] for entry in response.json()["schemas"]] == ["sample"]
            response = authenticated_client.get(
                reverse("mfss:power_circuit_schema", kwargs={"mine_dir": "mine_1", "filename": "link.json"})
            )
            assert response.status_code == 404
    finally:
        outside.unlink()


def test_schema_endpoints_reject_post(authenticated_client: Client) -> None:
    response = authenticated_client.post(reverse("mfss:power_circuit_schemas"))
    assert response.status_code == 405
    assert response["Cache-Control"] == "private, no-store"
