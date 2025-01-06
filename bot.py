import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis

from src.config import load_config
from src.database import get_sessionmaker
from src.handlers import main_router
from src.keyboards import set_main_menu

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info("Starting bot")

    config = load_config()
    properties = DefaultBotProperties(parse_mode="HTML")
    storage = RedisStorage(redis=Redis(host=config.redis.host, port=config.redis.port))

    bot = Bot(token=config.bot.token, default=properties)
    disp = Dispatcher(storage=storage)
    disp.include_router(main_router)

    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await disp.start_polling(bot, sessionmaker=get_sessionmaker())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(e)
