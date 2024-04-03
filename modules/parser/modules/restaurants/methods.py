import orjson

from core.modules.api.methods import API
from core.modules.logger.methods import logger
from modules.parser.modules.restaurants.config import HEADERS
from modules.parser.modules.restaurants.schemes import Restaurant, Location


class Parser:

    @staticmethod
    async def get_restaurants(location: Location) -> list[Restaurant]:
        response = await API.post(
            'https://eda.yandex.ru/eats/v1/layout-constructor/v1/layout',
            headers=HEADERS,
            json={'location': location.model_dump()}
        )

        if response.status_code != 200:
            logger.error(msg := f'Не удалось получить рестораны: {response}')
            raise ValueError(msg)

        content = orjson.loads(response.content)['data']

        result = set()

        try:
            result |= set(map(lambda x: Restaurant.model_validate(x), content['places_carousels'][0]['payload']['places']))
        except (IndexError, KeyError):
            pass

        try:
            result |= set(map(lambda x: Restaurant.model_validate(x), content['places_lists'][0]['payload']['places']))
        except (IndexError, KeyError):
            pass

        try:
            result |= set(map(lambda x: Restaurant.model_validate(x), content['places_lists'][1]['payload']['places']))
        except (IndexError, KeyError):
            pass

        return list(result)
