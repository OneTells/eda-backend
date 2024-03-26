import asyncio
from pprint import pprint

import orjson

from core.modules.api.methods import API
from modules.parser.modules.restaurants.config import HEADERS
from modules.parser.modules.restaurants.schemes import Restaurant, Location


class RestaurantsParser:

    @staticmethod
    async def execute(location: Location) -> list[Restaurant]:
        response = await API.post(
            'https://eda.yandex.ru/eats/v1/layout-constructor/v1/layout',
            headers=HEADERS,
            json={'location': location.model_dump()}
        )

        content = orjson.loads(response.content)['data']

        result = set()

        try:
            result |= set(map(lambda x: Restaurant.model_validate(x), content['places_carousels'][0]['payload']['places']))
        except KeyError:
            pass

        try:
            result |= set(map(lambda x: Restaurant.model_validate(x), content['places_lists'][0]['payload']['places']))
        except KeyError:
            pass

        try:
            result |= set(map(lambda x: Restaurant.model_validate(x), content['places_lists'][1]['payload']['places']))
        except KeyError:
            pass

        return list(result)


async def main():
    location = Location(
        latitude=56.838010,
        longitude=60.597465
    )

    result = await RestaurantsParser.execute(location)
    pprint([(hash(x), x) for x in result])

    await API.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
