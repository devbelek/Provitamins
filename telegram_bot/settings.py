from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import final
from decouple import config


@final
class Settings:
    debug: bool = config("DEBUG", cast=bool, default=False)
    redis_url: str = config("REDIS_URL", default="redis://localhost")
    bot_token: str = config("BOT_TOKEN", default="")
    base_webhook_url: str = config("BASE_WEBHOOK_URL", default="")
    webhook_path: str = config("WEBHOOK_PATH", default="")
    telegram_my_token: str = config("TELEGRAM_MY_TOKEN", default="")


@lru_cache()  # get it from memory
def get_settings() -> Settings:
    return Settings()
