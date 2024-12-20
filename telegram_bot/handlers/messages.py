from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold
from aiogram.types import Message
from asgiref.sync import sync_to_async
from loguru import logger

from telegram_bot.bot import telegram_router
from marketplace.models import TelegramUsername


@telegram_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    logger.info('STart received')
    user_id = message.from_user.id
    username = message.from_user.username
    await sync_to_async(TelegramUsername.objects.update_or_create)(telegram_id=user_id, defaults={"username": username})
    await message.answer(f"Здравствуйте, {hbold(message.from_user.full_name)}!\n" +
                        "Тут вы будете получать уведомления и информацию о заказах.")
