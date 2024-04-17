import random
from datetime import timedelta, datetime
from typing import Literal

from fastapi import APIRouter

from core.general.models.restaurants import Restaurants
from core.general.schemes.restaurant import Location
from core.modules.database.modules.requests.methods import Select
from modules.api.core.methods.distance import get_distance
from modules.api.modules.menu.methods import get_menu_by_restaurant_id
from modules.api.modules.menu.schemes import Menu

router = APIRouter(prefix='/menu')


@router.get("/random")
async def get_menu_for_random_restaurant(latitude: float, longitude: float,
                                         distance_type: Literal['delivary', 'near']) -> Menu | None:
    response = await (
        Select(Restaurants.id, Restaurants.longitude, Restaurants.latitude)
        .where(Restaurants.last_parsing_time + timedelta(days=3) > datetime.now())
        .fetch()
    )

    restaurant_id: int | None = None

    distance = 2000 if distance_type == 'delivary' else 500
    location = Location(latitude=latitude, longitude=longitude)

    while restaurant_id is None and response:
        restaurant = random.choice(response)

        d = get_distance(location, Location(latitude=restaurant['latitude'], longitude=restaurant['longitude']))

        if d <= distance:
            restaurant_id = restaurant['id']
        else:
            response.remove(restaurant)

    if not response:
        return

    return await get_menu_by_restaurant_id(restaurant_id)


@router.get("/{restaurant_id}")
async def get_menu(restaurant_id: int) -> Menu:
    return await get_menu_by_restaurant_id(restaurant_id)
