from typing import Literal, Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from core.general.schemes.restaurant import Location
from modules.api.core.methods.auth import authorization
from modules.api.core.schemes.api import Content
from modules.api.modules.menu.methods import get_menu_by_restaurant_id, get_random_restaurant_id
from modules.api.modules.menu.schemes import Menu

router = APIRouter(prefix='/menu', tags=['menu'])


@router.get("/random-restaurant", description='Получить меню рандомного ресторана')
async def get_menu_for_random_restaurant(
        latitude: float, longitude: float, distance_type: Literal['delivery', 'near'],
        user_id: Annotated[int | None, Depends(authorization)]
):
    radius = {'delivery': 2000, 'near': 500}[distance_type]
    location = Location(latitude=latitude, longitude=longitude)

    restaurant_id = await get_random_restaurant_id(radius, location)

    if restaurant_id:
        status_code = 200
        content = await get_menu_by_restaurant_id(user_id, restaurant_id)
    else:
        status_code = 404
        content = None

    return ORJSONResponse(content=Content[Menu](content=content).model_dump(), status_code=status_code)


@router.get("/{restaurant_id}", description='Получить меню ресторана по id')
async def get_menu(restaurant_id: int, user_id: Annotated[int | None, Depends(authorization)]):
    return ORJSONResponse(
        content=Content(content=await get_menu_by_restaurant_id(user_id, restaurant_id)).model_dump(),
        status_code=200
    )
