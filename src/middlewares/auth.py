from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from src.config import load_config
from src.database import User, get_sessionmaker

config = load_config()
cache = config.bot.cache


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            tg_user_id = event.from_user.id
            cached_user = await cache.get(f"user-{tg_user_id}")

            if not cached_user:
                async with get_sessionmaker()() as session:
                    async with session.begin():
                        user = await session.get(User, tg_user_id)

                        if user:
                            await cache.set(
                                f"user-{tg_user_id}", user.columns_to_dict(), "1h"
                            )
                            user = user.columns_to_dict()
            else:
                user = cached_user

            data["user"] = user
            return await handler(event, data)
