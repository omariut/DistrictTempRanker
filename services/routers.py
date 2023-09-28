from fastapi import APIRouter
import aiohttp
from services import utils
from fastapi import Request

service_routers = APIRouter(
    tags=["service"],
)


@service_routers.get("/coolest-districts/")
async def get_ten_coolest_dist():
    responses = await utils.get_district_temps()
    avg_district_temps = {
        str(response_data["longitude"])
        + "-"
        + str(response_data["latitude"]): await utils.get_location_avg_temp(
            response_data
        )
        for response_data in responses
    }
    sorted_avg_district_temps = sorted(avg_district_temps.items(), key=lambda x: x[1])
    ten_coolest_district = {item[0]: item[1] for item in sorted_avg_district_temps[:10]}
    return ten_coolest_district


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
        end_date = await utils.get_end_date(travel_date)
        url_to_get_user_temperature = await utils.get_weather_api(
            user_longitude, user_latitude, start_date=travel_date, end_date=end_date
        )
        url_to_get_destination_temperature = await utils.get_weather_api(
            destination_longitude,
            destination_latitude,
            start_date=travel_date,
            end_date=end_date,
        )

        async with aiohttp.ClientSession() as session:
            user_temperature = await utils.fetch_url(
                session, url_to_get_user_temperature
            )
            destination_temperature = await utils.fetch_url(
                session, url_to_get_destination_temperature
            )

        if user_temperature is None or destination_temperature is None:
            return {
                "message": "Failed to fetch temperature data. Please try again later."
            }

        user_location_avg_temp = await utils.get_location_avg_temp(user_temperature)
        destination_avg_temp = await utils.get_location_avg_temp(
            destination_temperature
        )

        if user_location_avg_temp < destination_avg_temp:
            base_url = f"http://{request.client.host}:{await utils.get_port(request)}"

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
