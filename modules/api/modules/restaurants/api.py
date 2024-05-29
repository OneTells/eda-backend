from datetime import timedelta, datetime

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from core.general.models.restaurants import Restaurants, Organizations
from core.general.schemes.restaurant import Location
from core.modules.database.methods.requests import Select
from modules.api.core.methods.distance import get_distance
from modules.api.core.schemes.api import Content
from modules.api.modules.restaurants.schemes import Restaurant

router = APIRouter(prefix='/restaurants', tags=['restaurants'])


@router.get("/nearest")
async def get_nearest_restaurants(latitude: float, longitude: float):
    response = await (
        Select(
            Restaurants.id, Organizations.name, Restaurants.rating, Organizations.photo,
            Restaurants.longitude, Restaurants.latitude
        ).join(Organizations, Restaurants.organization_id == Organizations.id)
        .where(Restaurants.last_parsing_time + timedelta(days=3) > datetime.now())
        .fetch()
    )

    location = Location(latitude=latitude, longitude=longitude)

    restaurants = []

    for restaurant in response:
        distance = get_distance(location, Location(latitude=restaurant['latitude'], longitude=restaurant['longitude']))

        if distance > 500:
            continue

        restaurants.append(
            Restaurant(
                id=restaurant[0],
                name=restaurant[1],
                rating=restaurant[2],
                distance=distance,
                photo=f'https://eda.yandex.ru/{restaurant[3]}'
            )
        )

    restaurants.sort(key=lambda x: x.distance)

    return ORJSONResponse(content=Content[list[Restaurant]](content=restaurants).model_dump(), status_code=200)
