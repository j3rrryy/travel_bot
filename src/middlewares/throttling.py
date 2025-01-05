import datetime
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class AntiFloodMiddleware(BaseMiddleware):
    time_updates = {}
    timedelta_limiter = datetime.timedelta(seconds=0.5)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            tg_user_id = event.from_user.id
            if tg_user_id in self.time_updates.keys():
                if (
                    datetime.datetime.now() - self.time_updates[tg_user_id]
                ) > self.timedelta_limiter:
                    self.time_updates[tg_user_id] = datetime.datetime.now()
                    return await handler(event, data)
            else:
                self.time_updates[tg_user_id] = datetime.datetime.now()
                return await handler(event, data)
