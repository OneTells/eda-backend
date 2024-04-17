from typing import Any

import orjson

from core.general.schemes.restaurant import Location
from core.general.utils.counter import FloodControl
from core.modules.logger.methods import logger
from core.modules.requests.core.methods import Requests
from modules.parsers.modules.restaurants.config import HEADERS
from modules.parsers.modules.restaurants.schemes import Restaurant, Organization, RestaurantAdditionalData


class RestaurantParser:
    __flood_control = FloodControl(250, minutes=1)

    @classmethod
    async def __get_additional_data(cls, restaurant_slug: str) -> RestaurantAdditionalData:
        await cls.__flood_control.wait_point()

        response = await Requests.get(
            f'https://eda.yandex.ru/api/v2/catalog/{restaurant_slug}',
            headers=HEADERS
        )

        if response.status_code != 200:
            logger.error(msg := f'Не удалось получить рестораны: {response}')
            raise ValueError(msg)

        content = orjson.loads(response.content)['payload']['foundPlace']['place']
        location = content['address']['location']

        return RestaurantAdditionalData(location['longitude'], location['latitude'], content['rating'])

    @classmethod
    async def __validate_restaurant(cls, element: dict) -> Restaurant:
        additional_data = await cls.__get_additional_data(element['slug'])

        return Restaurant(
            slug=element['slug'],
            organization=Organization(
                slug=element['brand']['slug'], name=element['name'], photo=element['media']['photos'][0]['uri']
            ), longitude=additional_data.longitude,
            latitude=additional_data.latitude,
            rating=additional_data.rating
        )

    @classmethod
    async def get_restaurants(cls, location: Location) -> list[Restaurant]:
        await cls.__flood_control.wait_point()

        response = await Requests.post(
            'https://eda.yandex.ru/eats/v1/layout-constructor/v1/layout',
            headers=HEADERS, json={'location': location.model_dump()}
        )

        if response.status_code == 404:
            return []

        if response.status_code != 200:
            logger.error(msg := f'Не удалось получить рестораны: {response}')
            raise ValueError(msg)

        content = orjson.loads(response.content)['data']

        if not content:
            return []

        result: set[Restaurant] = set()

        for places in (content.get('places_carousels', []) + content.get('places_lists', [])):
            try:
                restaurants = places['payload']['places']
            except KeyError:
                continue

            for restaurant in restaurants:
                result.add(await cls.__validate_restaurant(restaurant))

        return list(result)
