"""API_KEYS parsing and fail-closed validation in Settings.

Every Settings() here passes `_env_file=None` so a developer's local .env can't leak in.
"""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("API_KEYS", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)


def _key_values(cfg: Settings) -> list[str]:
    return [key.get_secret_value() for key in cfg.api_keys]


def test_api_keys_parsed_from_comma_separated_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_KEYS", "key-a,key-b")

    cfg = Settings(_env_file=None)

    assert _key_values(cfg) == ["key-a", "key-b"]


def test_api_keys_env_trims_whitespace_and_drops_empty_entries(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_KEYS", " key-a , ,key-b, ")

    cfg = Settings(_env_file=None)

    assert _key_values(cfg) == ["key-a", "key-b"]


def test_single_api_key_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_KEYS", "only-key")

    cfg = Settings(_env_file=None)

    assert _key_values(cfg) == ["only-key"]


def test_api_keys_are_masked_in_repr(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_KEYS", "super-secret-key")

    cfg = Settings(_env_file=None)

    assert "super-secret-key" not in repr(cfg)
    assert "super-secret-key" not in str(cfg.model_dump())


def test_local_environment_allows_no_api_keys():
    cfg = Settings(_env_file=None, environment="local")

    assert cfg.api_keys == []


@pytest.mark.parametrize("environment", ["development", "staging", "production"])
def test_non_local_environment_without_api_keys_fails_closed(environment: str):
    with pytest.raises(ValidationError, match="API_KEYS"):
        Settings(_env_file=None, environment=environment)


@pytest.mark.parametrize("environment", ["development", "staging", "production"])
def test_non_local_environment_with_only_blank_api_keys_fails_closed(
    monkeypatch: pytest.MonkeyPatch, environment: str
):
    monkeypatch.setenv("API_KEYS", " , ")

    with pytest.raises(ValidationError, match="API_KEYS"):
        Settings(_env_file=None, environment=environment)


def test_non_local_environment_with_api_keys_is_valid(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_KEYS", "prod-key")

    cfg = Settings(_env_file=None, environment="production")

    assert _key_values(cfg) == ["prod-key"]
