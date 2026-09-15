"""App settings. DATABASE_URL comes from the environment only — never
hardcode a connection string. Flag weights/thresholds are loaded from
config/weights.yaml at startup (CLAUDE.md rule 4: never in code)."""
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]
WEIGHTS_PATH = REPO_ROOT / "config" / "weights.yaml"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    database_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_weights() -> dict:
    with open(WEIGHTS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
