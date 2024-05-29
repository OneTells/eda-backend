import orjson

from core.general.utils.counter import FloodControl
from core.modules.logger.methods import logger
from core.modules.requests.methods.requests import Requests

from modules.parsers.modules.menu.config import HEADERS
from modules.parsers.modules.menu.schemes import Category, MenuItem


class MenuParser:
    __flood_control = FloodControl(250, minutes=1)

    @classmethod
    async def get_menu(cls, restaurant_slug: str) -> list[MenuItem]:
        await cls.__flood_control.async_wait_point()

        response = await Requests.get(
            f'https://eda.yandex.ru/api/v2/menu/retrieve/{restaurant_slug}',
            headers=HEADERS
        )

        if response.status_code != 200:
            logger.error(msg := f'Не удалось получить меню: {response}')
            raise ValueError(msg)

        categories = orjson.loads(response.content)['payload']['categories']

        result: set[MenuItem] = set()

        for category in map(Category.model_validate, categories):
            for item in category.items:
                result.add(
                    MenuItem(
                        category_name=category.name,
                        name=item.name,
                        description=item.description,
                        price=item.price,
                        nutrients=item.nutrients,
                        measure=item.measure,
                        photo=item.picture.uri if item.picture else None
                    )
                )

        return list(result)
