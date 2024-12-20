import django
from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger

from telegram_bot.routes import root_router
from telegram_bot.settings import get_settings

import os
from importlib.util import find_spec

from vitamins.wsgi import get_wsgi_application
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.staticfiles import StaticFiles


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vitamins.settings")
django.setup()

from telegram_bot import handlers


cfg = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("🚀 Starting application")
    from telegram_bot.bot import start_telegram
    await start_telegram()
    yield
    logger.info("⛔ Stopping application")

app = FastAPI(lifespan=lifespan)
app.include_router(root_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)



