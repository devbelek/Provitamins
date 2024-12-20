from __future__ import annotations
from typing import Annotated, Union, TypeVar
from loguru import logger
from aiogram import types
from fastapi import APIRouter, Header
from telegram_bot.settings import get_settings
from telegram_bot.bot import bot, dp

T = TypeVar('T')
Response = Union[None, dict]

cfg = get_settings()

root_router = APIRouter(
    prefix="",
    tags=["root"],
    responses={404: {"description": "Not found"}},
)


@root_router.get("/")
async def root() -> dict:
    return {"message": "Hello World"}


@root_router.post(cfg.webhook_path)
async def bot_webhook(update: dict,
                      x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None) -> None | dict:
    """ Register webhook endpoint for telegram telegram_bot"""
    if x_telegram_bot_api_secret_token != cfg.telegram_my_token:
        logger.error("Wrong secret token !")
        return {"status": "error", "message": "Wrong secret token !"}
    telegram_update = types.Update(**update)
    logger.info(f"Update: {telegram_update}")
    await dp.feed_webhook_update(bot=bot, update=telegram_update)
