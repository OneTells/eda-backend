import orjson

from core.general.schemes.restaurant import Location
from core.general.utils.counter import FloodControl
from core.modules.logger.methods import logger
from core.modules.requests.core.methods import Requests
from modules.parsers.modules.restaurants.config import HEADERS
from modules.parsers.modules.restaurants.schemes import Restaurant


class RestaurantParser:
    __flood_control = FloodControl(250, minutes=1)

    @classmethod
    async def get_restaurants(cls, location: Location) -> list[Restaurant]:
        await cls.__flood_control.wait_point()

        response = await Requests.post(
            'https://eda.yandex.ru/eats/v1/layout-constructor/v1/layout',
            headers=HEADERS, json={'location': location}
        )

        if response.status_code != 200:
            logger.error(msg := f'Не удалось получить рестораны: {response}')
            raise ValueError(msg)

        content = orjson.loads(response.content)['data']

        if not content:
            return []

        result = set()

        for places in (content.get('places_carousels', []) + content.get('places_lists', [])):
            try:
                result |= set(map(Restaurant.model_validate, places['payload']['places']))
            except (IndexError, KeyError):
                pass

        return list(result)

    @classmethod
    async def add_additional_data(cls, restaurant: Restaurant) -> None:
        await cls.__flood_control.wait_point()

        response = await Requests.get(
            f'https://eda.yandex.ru/api/v2/catalog/{restaurant.slug}',
            headers=HEADERS
        )

        if response.status_code != 200:
            logger.error(msg := f'Не удалось получить рестораны: {response}')
            raise ValueError(msg)

        content = orjson.loads(response.content)['payload']['foundPlace']['place']

        restaurant.rating = content['rating']

        location = content['address']['location']
        restaurant.longitude = location['longitude']
        restaurant.latitude = location['latitude']
