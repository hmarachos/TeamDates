from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change_me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///birthdays.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024

    SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "25"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = env_bool("SMTP_USE_TLS")
    SMTP_TIMEOUT = int(os.getenv("SMTP_TIMEOUT", "10"))
    MAIL_FROM = os.getenv("MAIL_FROM", "birthday-reminder@example.local")

    MONTHLY_NOTIFICATION_DAY = int(os.getenv("MONTHLY_NOTIFICATION_DAY", "25"))
    MONTHLY_NOTIFICATION_HOUR = int(os.getenv("MONTHLY_NOTIFICATION_HOUR", "9"))
    DAILY_NOTIFICATION_HOUR = int(os.getenv("DAILY_NOTIFICATION_HOUR", "9"))

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change_me_now")

    LOG_FILE = str(BASE_DIR / "logs" / "app.log")


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SCHEDULER_ENABLED = False

