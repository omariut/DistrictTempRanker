from datetime import datetime, timedelta
from services.districts import (
    district_data,
)  # Import district_data from a module named services.districts
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

    return f"{base_url}?{query_params}"  # Construct and return the weather API URL


async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()


async def fetch_multiple_urls(urls):
    async with aiohttp.ClientSession() as session:

        tasks = [fetch_url(session, url) for url in urls]

        responses = await asyncio.gather(*tasks)

    return responses


async def fetch_single_url(url):
    async with aiohttp.ClientSession() as session:
        return await fetch_url(session, url)


async def get_temperature(longitude, latitude, start_date, end_date):
    url = await get_weather_api(longitude, latitude, start_date, end_date)
    return await fetch_single_url(url)


async def get_district_temps():
    # Create a list of weather API URLs for each district
    # Instead of API calling district data are collected from a file as the data is fixed and it improves performance
    urls = [await get_weather_api(item["long"], item["lat"]) for item in district_data]
    return await fetch_multiple_urls(urls)


async def get_location_avg_temp(response_data):
    print(response_data)
    temps_list = response_data["hourly"]["temperature_2m"]

    # Extract temperatures at 2 PM for the next 7 days
    # The 'temps_list' contains temperature data for multiple hours over several days.
    # To get temperatures at 2 PM for the next 7 days, we need to extract specific elements
    # from 'temps_list' using indexing.

    # We start from the 14th element in 'temps_list' because each day has 24 hours of data,
    # and 2 PM is the 14th hour of the day (0-based index).

    # We use a list comprehension to efficiently extract temperatures at 2 PM for the next 7 days.
    # 'i' represents the day index, ranging from 0 to 6 (0-indexed), corresponding to the next 7 days.
    # For each day, we calculate the index for 2 PM using '14 + (i * 24)'.
    # - '14' is the starting hour for 2 PM.
    # - 'i * 24' advances to the appropriate day's data (0-24 hours for each day).

    # The result is a list of temperatures at 2 PM for the next 7 days.
    temps_list_at_2_pm = [temps_list[14 + (i * 24)] for i in range(7)]

    # This indexing approach is efficient because it avoids iterating through unnecessary
    # data points and directly extracts the relevant temperatures for the specified hours.

    # Calculate the average temperature at 2 PM
    avg = sum(temps_list_at_2_pm) / 7
    return avg  # Return the average temperature


async def get_end_date(travel_date: str):
    travel_date_obj = datetime.strptime(travel_date, "%Y-%m-%d")
    end_date_obj = travel_date_obj + timedelta(days=7)
    end_date = end_date_obj.strftime("%Y-%m-%d")
    return end_date  # Calculate and return the end date 7 days from the travel date


async def get_port(request: Request):
    scope = request.scope
    server_info = scope.get("server", {})
    port = server_info[-1]  # Extract the port information from the server scope
    return port  # Return the port information


async def get_recommendation(user_location_avg_temp, destination_avg_temp, request):
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

    return recommendation
