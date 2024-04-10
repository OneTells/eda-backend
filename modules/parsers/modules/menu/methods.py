import orjson

from core.modules.logger.methods import logger
from core.modules.requests.core.methods import Requests
from modules.parsers.modules.menu.config import HEADERS
from modules.parsers.modules.menu.schemes import Item


class Parser:

    @staticmethod
    async def get_menu(slug: str) -> list[Item]:
        response = await Requests.get(
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