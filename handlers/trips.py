from asyncio import BoundedSemaphore
from datetime import date
from datetime import datetime as dt

import aiofiles.os as aos
import aioshutil as ash
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from config_data import Config, load_config
from database import create_update_trip, delete_trip_db, get_trip_db
from errors import DatabaseError, GeocodingError, IsStartPointError
from external_services import convert_coordinates
from keyboards import (
    confirm_trip_deletion_kb,
    leave_blank_kb,
    leave_same_kb,
    my_trips_kb,
    paginator_kb,
    trip_options_kb,
)
from lexicon import ERROR_LEXICON_RU, KB_LEXICON_RU, LEXICON_RU
from services import create_trip_info
from states import FSMTrip

trip_router: Router = Router()
config: Config = load_config()
semaphore: BoundedSemaphore = config.tg_bot.semaphore


@trip_router.callback_query(
    F.data.func(lambda x: "trips-page-" in x),
    StateFilter(default_state),
)
async def trips(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send active trips.
    """

    await callback.answer()
    data = callback.data.split("-")

    try:
        await callback.message.edit_text(
            LEXICON_RU["my_trips"],
            reply_markup=(
                await paginator_kb(user, int(data[-1]), "trips", sessionmaker)
            ),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@trip_router.callback_query(
    F.data.func(lambda x: "trip-" in x and x.count("-") == 1),
    StateFilter(default_state),
)
async def get_trip(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Send the trip info with edit and delete buttons.
    """

    try:
        await callback.answer()
        trip_id = int(callback.data.split("-")[-1])
        selected_trip_info = await get_trip_db(trip_id, sessionmaker)
        await callback.message.edit_text(
            create_trip_info(selected_trip_info),
            reply_markup=trip_options_kb(
                trip_id,
                user["username"] == selected_trip_info["username"],
            ),
        )
    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@trip_router.callback_query(F.data == "new_trip", StateFilter(default_state))
async def new_trip(callback: CallbackQuery, user: dict, state: FSMContext):
    """
    Let the user create a new trip and set its name.
    """

    try:
        await callback.answer()
        await callback.message.edit_text(LEXICON_RU["new_trip"])
        await state.update_data(username=user["username"])
        await state.set_state(FSMTrip.set_name)
    except:
        await state.clear()
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@trip_router.message(F.text, StateFilter(FSMTrip.set_name))
async def trip_name(message: Message, state: FSMContext):
    """
    Set trip name and send a message
    which allows the user to set its description.
    """

    try:
        await message.answer(
            LEXICON_RU["trip_description"], reply_markup=leave_blank_kb()
        )
        await state.update_data(name=message.text)
        await state.set_state(FSMTrip.set_descriptipon)
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@trip_router.message(F.text, StateFilter(FSMTrip.set_descriptipon))
async def trip_description(message: Message, state: FSMContext):
    """
    Set trip description and send a message
    which allows the user to set its destination.
    """

    try:
        await message.answer(LEXICON_RU["trip_destination"])

        if message.text != KB_LEXICON_RU["leave_blank"]:
            await state.update_data(description=message.text)
        else:
            await state.update_data(description="")

        await state.set_state(FSMTrip.set_destination)
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@trip_router.message(F.location, StateFilter(FSMTrip.set_destination))
async def trip_destination(message: Message, user: dict, state: FSMContext):
    """
    Set trip destination and send a message
    which allows the user to set its dates.
    """

    try:
        latitude = round(message.location.latitude, 3)
        longitude = round(message.location.longitude, 3)

        if user["latitude"] == latitude and user["longitude"] == longitude:
            raise IsStartPointError

        res = await convert_coordinates(latitude, longitude)

        if res:
            country, city = res[0], res[1]
            await message.answer(LEXICON_RU["trip_dates"])
            await state.update_data(
                locations=[
                    {
                        "country": country,
                        "city": city,
                        "latitude": latitude,
                        "longitude": longitude,
                    }
                ]
            )
            await state.set_state(FSMTrip.set_dates)
        else:
            await message.answer(ERROR_LEXICON_RU["GeocodingError"])

    except IsStartPointError:
        await message.answer(ERROR_LEXICON_RU["IsStartPointError"])
    except GeocodingError:
        await message.answer(ERROR_LEXICON_RU["GeocodingError"])
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@trip_router.message(F.text, StateFilter(FSMTrip.set_dates))
async def trip_dates(
    message: Message, state: FSMContext, sessionmaker: async_sessionmaker[AsyncSession]
):
    """
    Set trip dates and send a button with trips.
    """

    try:
        d1, d2 = map(
            lambda date: dt.strptime(date, "%d.%m.%Y"), message.text.split("-")
        )

        if date(d1.year, d1.month, d1.day) >= date.today() and d2 > d1:
            data = await state.get_data()
            data["dates"] = [
                d1.strftime("%d.%m.%Y"),
                d2.strftime("%d.%m.%Y"),
            ]
            await create_update_trip(data, sessionmaker)
            await message.answer(LEXICON_RU["trip_created"], reply_markup=my_trips_kb())
            await state.clear()
        else:
            await message.answer(ERROR_LEXICON_RU["incorrect_data"])

    except DatabaseError:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await message.answer(ERROR_LEXICON_RU["incorrect_data"])


@trip_router.callback_query(
    F.data.func(lambda x: "edit-trip-" in x), StateFilter(default_state)
)
async def edit_trip(callback: CallbackQuery, state: FSMContext):
    """
    Let the user edit the name of the trip.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.answer(
            LEXICON_RU["edit_trip"], reply_markup=leave_same_kb()
        )
        await state.update_data(id=int(data[-1]))
        await state.set_state(FSMTrip.edit_name)
    except:
        await state.clear()
        await callback.message.answer(ERROR_LEXICON_RU["InternalError"])


@trip_router.message(F.text, StateFilter(FSMTrip.edit_name))
async def edit_trip_name(message: Message, state: FSMContext):
    """
    Edit trip name and send a message
    which allows the user to edit its description.
    """

    try:
        await message.answer(
            LEXICON_RU["edit_description"],
            reply_markup=leave_same_kb(with_blank=True),
        )

        if message.text != KB_LEXICON_RU["leave_same"]:
            await state.update_data(name=message.text)

        await state.set_state(FSMTrip.edit_descriptipon)
    except:
        await state.clear()
        await message.edit_text(ERROR_LEXICON_RU["InternalError"])


@trip_router.message(F.text, StateFilter(FSMTrip.edit_descriptipon))
async def edit_trip_description(
    message: Message,
    state: FSMContext,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    """
    Edit trip description and send a back button.
    """
    try:
        data = await state.get_data()

        if message.text not in (
            KB_LEXICON_RU["leave_blank"],
            KB_LEXICON_RU["leave_same"],
        ):
            data["description"] = message.text
        elif message.text == KB_LEXICON_RU["leave_blank"]:
            data["description"] = ""

        trip_id = data["id"]
        await create_update_trip(data, sessionmaker)
        trip = await get_trip_db(trip_id, sessionmaker)

        await message.answer(
            LEXICON_RU["editing_done"] + "\n\n" + create_trip_info(trip),
            reply_markup=trip_options_kb(trip_id, user["username"] == trip["username"]),
        )
        await state.clear()

    except DatabaseError:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await state.clear()
        await message.answer(ERROR_LEXICON_RU["InternalError"])


@trip_router.callback_query(
    F.data.func(lambda x: "pre-delete-trip-" in x), StateFilter(default_state)
)
async def pre_delete_trip(callback: CallbackQuery):
    """
    Let the user delete the trip.
    """

    try:
        await callback.answer()
        data = callback.data.split("-")
        await callback.message.edit_text(
            LEXICON_RU["confirm_deletion"],
            reply_markup=confirm_trip_deletion_kb(int(data[-1])),
        )
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@trip_router.callback_query(
    F.data.func(lambda x: "finally-delete-trip-" in x), StateFilter(default_state)
)
async def finally_delete_trip(
    callback: CallbackQuery,
    user: dict,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    try:
        await callback.answer()
        data = callback.data.split("-")
        trip_id = int(data[-1])
        await delete_trip_db(trip_id, sessionmaker)
        await callback.message.edit_text(
            LEXICON_RU["deletion_done"], reply_markup=my_trips_kb()
        )

        async with semaphore:
            path = f"./files/{user["id"]}/{trip_id}/"

            if await aos.path.exists(path):
                await ash.rmtree(path, ignore_errors=True)

    except DatabaseError:
        await callback.message.edit_text(ERROR_LEXICON_RU["DatabaseError"])
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])


@trip_router.callback_query(
    F.data == "cancel-trip-deletion", StateFilter(default_state)
)
async def cancel_trip_deletion(callback: CallbackQuery):
    try:
        await callback.answer()
        await callback.message.edit_text(
            LEXICON_RU["deletion_canceled"], reply_markup=my_trips_kb()
        )
    except:
        await callback.message.edit_text(ERROR_LEXICON_RU["InternalError"])
