from aiogram import Router

from src.middlewares import AntiFloodMiddleware, AuthMiddleware

from .expenses import *  # noqa: F403
from .friends import *  # noqa: F403
from .locations import *  # noqa: F403
from .notes import *  # noqa: F403
from .trips import *  # noqa: F403
from .users import *  # noqa: F403
from .utils import *  # noqa: F403

main_router = Router()
main_router.include_routers(
    user_router,  # noqa: F405
    trip_router,  # noqa: F405
    location_router,  # noqa: F405
    friend_router,  # noqa: F405
    note_router,  # noqa: F405
    expense_router,  # noqa: F405
    utils_router,  # noqa: F405
)

main_router.message.middleware.register(AuthMiddleware())
main_router.callback_query.middleware.register(AuthMiddleware())
main_router.message.middleware.register(AntiFloodMiddleware())
main_router.callback_query.middleware.register(AntiFloodMiddleware())
