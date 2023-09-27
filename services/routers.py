from typing import List
import time
import asyncio
from fastapi import Depends, FastAPI, HTTPException
from fastapi import APIRouter
from services.districts import district_data
import aiohttp
from services.sample_data import sample_data

service_routers = APIRouter(
    tags=["service"],
)


async def get_weather_api(longitude, latitude):
    return "https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&hourly=temperature_2m"


async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()


async def get_district_temps():
    urls = [
        await get_weather_api(item["longitude"], item["latitude"])
        for item in district_data
    ]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)
    return responses


async def get_district_avg_temp(response_data=sample_data):
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
        + str(response_data["latitude"]): await get_district_avg_temp(response_data)
        for response_data in responses
    }
    sorted_avg_district_temps = sorted(avg_district_temps.items(), key=lambda x: x[1])
    ten_coolest_district = {item[0]: item[1] for item in sorted_avg_district_temps[:10]}
    return ten_coolest_district
