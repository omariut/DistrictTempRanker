from fastapi import APIRouter
import aiohttp
from services import utils
from fastapi import Request

service_routers = APIRouter(
    tags=["service"],
)


@service_routers.get("/coolest-districts")
async def get_ten_coolest_dist():
    responses = await utils.get_district_temps()

    avg_district_temps = [
        {
            "longitude": response_data["longitude"],
            "latitude": response_data["latitude"],
            "avg_temperature": await utils.get_location_avg_temp(response_data),
        }
        for response_data in responses
    ]

    sorted_avg_district_temps = sorted(
        avg_district_temps, key=lambda x: x["avg_temperature"]
    )
    ten_coolest_district = sorted_avg_district_temps[:10]

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
        user_temperature = await utils.get_temperature(
            user_longitude, user_latitude, start_date=travel_date, end_date=end_date
        )
        destination_temperature = await utils.get_temperature(
            destination_longitude,
            destination_latitude,
            start_date=travel_date,
            end_date=end_date,
        )

        if user_temperature is None or destination_temperature is None:
            return {
                "message": "Failed to fetch temperature data. Please try again later."
            }

        user_location_avg_temp = await utils.get_location_avg_temp(user_temperature)
        destination_avg_temp = await utils.get_location_avg_temp(
            destination_temperature
        )

        recommendation = await utils.get_recommendation(
            user_location_avg_temp, destination_avg_temp, request
        )

        return {
            "user_temperature_2pm": user_location_avg_temp,
            "destination_temperature_2pm": destination_avg_temp,
            "recommendation": recommendation,
        }
    except Exception as e:
        return {"message": str(e)}
