from datetime import datetime, timedelta
from services.districts import district_data
from fastapi import Request
import aiohttp
import asyncio


async def get_weather_api(longitude, latitude, start_date=None, end_date=None):
    base_url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
        "hourly": "temperature_2m",
    }

    if start_date and end_date:
        params.update({"start_date": start_date, "end_date": end_date})

    query_params = "&".join(f"{key}={value}" for key, value in params.items())

    return f"{base_url}?{query_params}"


async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()


async def get_district_temps():
    urls = [await get_weather_api(item["long"], item["lat"]) for item in district_data]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)
    return responses


async def get_location_avg_temp(response_data):
    temps_list = response_data["hourly"]["temperature_2m"]
    temps_list_at_2_pm = [temps_list[14 + (i * 24)] for i in range(7)]
    avg = sum(temps_list_at_2_pm) / 7
    return avg


async def get_end_date(travel_date: str):
    travel_date_obj = datetime.strptime(travel_date, "%Y-%m-%d")
    end_date_obj = travel_date_obj + timedelta(days=7)
    end_date = end_date_obj.strftime("%Y-%m-%d")
    return end_date


async def get_port(request: Request):
    scope = request.scope
    server_info = scope.get("server", {})
    port = server_info[-1]
    return port
