from aiogram import Router

from middlewares import *

from .expenses import *
from .friends import *
from .locations import *
from .notes import *
from .trips import *
from .users import *
from .utils import *

main_router = Router()
main_router.include_routers(
    user_router,
    trip_router,
    location_router,
    friend_router,
    note_router,
    expense_router,
    utils_router,
)

main_router.message.middleware.register(AuthMiddleware())
main_router.callback_query.middleware.register(AuthMiddleware())
main_router.message.middleware.register(AntiFloodMiddleware())
main_router.callback_query.middleware.register(AntiFloodMiddleware())
