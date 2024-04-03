import asyncio

from core.general.models.menu import MenuItems
from core.general.models.restaurants import Restaurants
from core.general.utils.counter import TimeCounter
from core.modules.database.methods import Insert, Select
from core.modules.worker.abstract.executor import BaseExecutor
from core.modules.worker.abstract.trigger import BaseTrigger
from core.modules.worker.abstract.worker import BaseWorker
from core.modules.worker.schemes.setting import Setting
from core.modules.worker.utils.timer import timer
from modules.parser.modules.menu.methods import Parser


class Executor(BaseExecutor):
    __time_counter = TimeCounter(minutes=1)

    @classmethod
    async def __flood_control(cls):
        if cls.__time_counter.add() >= 20:
            await asyncio.sleep(cls.__time_counter.time_until_element_is_deleted)

    async def __call__(self, restaurant_id: int, restaurant_slug: str) -> None:
        await self.__flood_control()

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
