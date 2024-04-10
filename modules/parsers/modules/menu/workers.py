from datetime import datetime

from core.general.models.menu import MenuItems, Categories
from core.general.models.restaurants import Restaurants
from core.modules.database.methods import Insert, Select, Delete
from core.modules.logger.methods import logger
from core.modules.worker.abstract.executor import BaseExecutor
from core.modules.worker.abstract.trigger import BaseTrigger
from core.modules.worker.abstract.worker import BaseWorker
from core.modules.worker.schemes.setting import Setting
from core.modules.worker.utils.timer import timer
from modules.parsers.modules.menu.methods import MenuParser
from modules.parsers.modules.menu.schemes import MenuItem


class Executor(BaseExecutor):

    @staticmethod
    async def __get_category_id(menu_item: MenuItem) -> int:
        category_id: int | None = await (
            Select(Categories.id)
            .where(Categories.name == menu_item.category_name)
            .fetch_one(model=lambda x: x[0])
        )

        if category_id is not None:
            return category_id

        category_id = await (
            Insert(Categories)
            .values(name=menu_item.category_name)
            .returning(Categories.id, model=lambda x: x[0])
        )

        if category_id is None:
            logger.error(msg := 'Не удалось добавить категорию')
            raise ValueError(msg)

        return category_id

    async def __call__(self, restaurant_id: int, restaurant_slug: str) -> None:
        menu_items = await MenuParser.get_menu(restaurant_slug)

        new_menu_items: list[dict[str, [str, None, datetime]]] = []
        current_time = datetime.now()

        for menu_item in menu_items:
            try:
                category_id = await self.__get_category_id(menu_item)
            except ValueError:
                continue

            new_menu_items.append(
                {
                    'category_id': category_id,
                    'name': menu_item.name,
                    'description': menu_item.description,
                    'price': menu_item.price,
                    'nutrient': menu_item.nutrients.model_dump_json() if menu_item.nutrients else None,
                    'measure': menu_item.measure.model_dump_json() if menu_item.measure else None,
                    'photo': menu_item.photo,
                    'restaurant_id': restaurant_id,
                    'last_parsing_time': current_time
                }
            )

        # todo Использовать транзакции и __переделать__

        await (
            Delete(MenuItems)
            .where(MenuItems.restaurant_id == restaurant_id)
            .execute()
        )

        for result_ in (new_menu_items[n:n + 50] for n in range(0, len(new_menu_items), 50)):
            await Insert(MenuItems).values(result_).execute()


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
