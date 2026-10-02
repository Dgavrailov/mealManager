"""Load configuration from .env file (stdlib only, no python-dotenv)."""

import os
from pathlib import Path

_ENV_PATH = Path(__file__).resolve().parent / ".env"


def _load_env() -> dict:
    env = {}
    if _ENV_PATH.exists():
        for line in _ENV_PATH.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            val = val.split(" #", 1)[0]  # strip a trailing ' # comment', if any
            env[key.strip()] = val.strip()
    return env


_cfg = _load_env()


def get(key: str, default: str = "") -> str:
    return os.environ.get(key, _cfg.get(key, default))


SMTP_USER    = get("SMTP_USER")
SMTP_PASS    = get("SMTP_PASS")
SMTP_FROM    = get("SMTP_FROM") or SMTP_USER
SMTP_HOST    = get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT    = int(get("SMTP_PORT", "587"))
SECRET_KEY   = get("SECRET_KEY", "change-me")
APP_BASE_URL = get("APP_BASE_URL", "")   # e.g. http://10.6.150.107:8000
