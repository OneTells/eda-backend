from typing import List

from asyncpg import Record

from core.general.models.menu import MenuItems
from core.general.models.restaurants import Restaurants
from core.modules.database.methods import Insert, Select
from core.modules.worker.abstract.executor import BaseExecutor
from core.modules.worker.abstract.trigger import BaseTrigger
from core.modules.worker.abstract.worker import BaseWorker
from core.modules.worker.schemes.setting import Setting
from core.modules.worker.utils.timer import timer
from modules.parser.modules.menu.methods import Parser


class Executor(BaseExecutor):

    async def __call__(self, restaurant_id: int, restaurant_slug: str) -> None:
        menu_items = await Parser.get_menu(restaurant_slug)
        result = []

        for item in menu_items:
            result.append(
                {
                    'name': item.name,
                    'description': item.description,
                    'price': item.price,
                    'nutrient': item.nutrients.model_dump_json() if item.nutrients else None,
                    'weight_in_grams': item.measure.value if item.measure else None,
                    'photo': item.picture.uri if item.picture else None,
                    'restaurant_id': restaurant_id
                }
            )

        await Insert(MenuItems).values(result).execute()


class Trigger(BaseTrigger):

    async def __call__(self) -> list[tuple]:
        return await Select(Restaurants.id, Restaurants.slug).fetch(model=tuple)


class MenuItemSearcherWorker(BaseWorker):

    @staticmethod
    def setting() -> Setting:
        return Setting(timeout=timer(hours=12), worker_count=1)

    @staticmethod
    def executor() -> type[BaseExecutor]:
        return Executor

    @staticmethod
    def trigger() -> type[BaseTrigger]:
        return Trigger
