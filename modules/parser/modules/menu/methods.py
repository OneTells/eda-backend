from pprint import pprint

import orjson
import asyncio

from core.modules.api.methods import API
from core.modules.logger.methods import logger
from modules.parser.modules.menu.config import HEADERS
from modules.parser.modules.menu.schemes import Item


class Parser:

    @staticmethod
    async def get_menu(slug: str) -> list[Item]:
        response = await API.get(
            f'https://eda.yandex.ru/api/v2/menu/retrieve/{slug}', headers=HEADERS
        )

        if response.status_code != 200:
            logger.error(msg := f'Не удалось получить меню: {response}')
            raise ValueError(msg)

        content = orjson.loads(response.content)['payload']

        result = set()

        for category in content['categories']:
            try:
                result |= set(map(lambda x: Item.model_validate(x), category['items']))
            except KeyError:
                pass

        return list(result)

async def main():
    parser = Parser()
    l = await parser.get_menu('gyros__bistro')
    pprint(l)


if __name__ == '__main__':
    asyncio.run(main())
