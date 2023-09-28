from typing import List
import time
import asyncio
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi import APIRouter
from services.districts import district_data
import aiohttp
from services.sample_data import sample_data
from datetime import datetime, timedelta


service_routers = APIRouter(
    tags=["service"],
)


async def get_weather_api(longitude, latitude, start_date="", end_date=""):
    base_url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
        "hourly": "temperature_2m",
        "start_date": start_date,
        "end_date": end_date,
    }

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


@service_routers.get("/coolest-districts/")
async def get_ten_coolest_dist():
    # not tested yet
    responses = await get_district_temps()
    avg_district_temps = {
        str(response_data["longitude"])
        + "-"
        + str(response_data["latitude"]): await get_location_avg_temp(response_data)
        for response_data in responses
    }
    sorted_avg_district_temps = sorted(avg_district_temps.items(), key=lambda x: x[1])
    ten_coolest_district = {item[0]: item[1] for item in sorted_avg_district_temps[:10]}
    return ten_coolest_district


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


@service_routers.get("/travel-advice")
async def travel_advice(
    user_longitude: float,
    user_latitude: float,
    destination_longitude: float,
    destination_latitude: float,
    travel_date: str,
    request: Request,
):
    try:
        end_date = await get_end_date(travel_date)
        url_to_get_user_temperature = await get_weather_api(
            user_longitude, user_latitude, start_date=travel_date, end_date=end_date
        )
        url_to_get_destination_temperature = await get_weather_api(
            destination_longitude,
            destination_latitude,
            start_date=travel_date,
            end_date=end_date,
        )

        async with aiohttp.ClientSession() as session:
            user_temperature = await fetch_url(session, url_to_get_user_temperature)
            destination_temperature = await fetch_url(
                session, url_to_get_destination_temperature
            )

        if user_temperature is None or destination_temperature is None:
            return {
                "message": "Failed to fetch temperature data. Please try again later."
            }

        user_location_avg_temp = await get_location_avg_temp(user_temperature)
        destination_avg_temp = await get_location_avg_temp(destination_temperature)

        if user_location_avg_temp < destination_avg_temp:
            base_url = f"http://{request.client.host}:{await get_port(request)}"

            recommendation = (
                "If you're looking for cooler temperatures, "
                f"it's actually warmer at the destination. "
                "You might want to consider other options if you prefer cooler weather. "
                f"Check out the coolest districts here: {base_url}/coolest-districts/ and choose a place to travel."
            )

        elif user_location_avg_temp > destination_avg_temp:
            recommendation = (
                "It's cooler at the destination. Might be a good place to travel."
            )
        else:
            recommendation = "Temperatures are similar!"

        return {
            "user_temperature_2pm": user_location_avg_temp,
            "destination_temperature_2pm": destination_avg_temp,
            "recommendation": recommendation,
        }
    except Exception as e:
        return {"message": str(e)}
