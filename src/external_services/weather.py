from datetime import date, timedelta
from datetime import datetime as dt

from aiohttp import ClientSession
from cashews import cache

from src.errors import ServiceConnectionError, WeatherDateError


@cache(ttl="6h")
async def get_weather_forecast(
    start_date: dt,
    end_date: dt,
    location_latitude: float,
    location_longitude: float,
) -> str:
    """
    Create a weather forecast for location in the trip.
    """

    start_dt = date(start_date.year, start_date.month, start_date.day)
    end_dt = date(end_date.year, end_date.month, end_date.day)

    if date.today() + timedelta(days=16) < start_dt:
        raise WeatherDateError

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location_latitude,
        "longitude": location_longitude,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "wind_speed_10m_max",
        ],
        "wind_speed_unit": "ms",
        "forecast_days": 16,
    }
    res = ""

    try:
        async with ClientSession() as session:
            async with session.get(url, params=params) as response:
                forecast = (await response.json())["daily"]

        for day_date, max_t, min_t, precip, wind in zip(
            forecast["time"],
            forecast["temperature_2m_max"],
            forecast["temperature_2m_min"],
            forecast["precipitation_sum"],
            forecast["wind_speed_10m_max"],
        ):
            pre_res = ""
            dt_decode = dt.strptime(day_date, "%Y-%m-%d")
            day_date = date(dt_decode.year, dt_decode.month, dt_decode.day)

            if start_dt <= day_date and day_date <= end_dt:
                pre_res += f"\U0001f4c5 Дата: {day_date.strftime('%d.%m.%Y')}\n"
                pre_res += (
                    "\U0001f321 Макс. и мин. температура: " + f"{max_t} / {min_t} °C\n"
                )
                pre_res += f"\U000026c8 Осадки: {precip} мм\n"
                pre_res += f"\U0001f32c Макс. скорость ветра: {wind} м/с\n\n"

            res += pre_res

    except Exception as e:
        raise ServiceConnectionError from e

    return res
