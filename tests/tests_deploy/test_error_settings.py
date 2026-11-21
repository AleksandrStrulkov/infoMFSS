from __future__ import annotations

import importlib

import pytest


def test_additional_hosts_and_origins_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    import config.settings as project_settings

    monkeypatch.setenv("ALLOWED_HOSTS", "203.0.113.10, example.test")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "http://203.0.113.10, https://example.test")
    try:
        importlib.reload(project_settings)
        assert "203.0.113.10" in project_settings.ALLOWED_HOSTS
        assert "example.test" in project_settings.ALLOWED_HOSTS
        assert "http://203.0.113.10" in project_settings.CSRF_TRUSTED_ORIGINS
        assert "https://example.test" in project_settings.CSRF_TRUSTED_ORIGINS
    finally:
        monkeypatch.delenv("ALLOWED_HOSTS")
        monkeypatch.delenv("CSRF_TRUSTED_ORIGINS")
        importlib.reload(project_settings)
