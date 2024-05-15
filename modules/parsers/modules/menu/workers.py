from datetime import datetime

from core.general.models.menu import MenuItems, Categories
from core.general.models.restaurants import Restaurants
from core.general.schemes.menu import Nutrients, Measure
from core.modules.database.modules.requests.methods import Select, Insert, Update
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

    @staticmethod
    async def __get_menu_items_in_db(restaurant_id) -> dict[str, MenuItem]:
        response = await (
            Select(
                MenuItems.name, MenuItems.description, MenuItems.price, MenuItems.nutrients,
                MenuItems.measure, MenuItems.photo, Categories.name
            ).join(Categories, MenuItems.category_id == Categories.id)
            .where(MenuItems.restaurant_id == restaurant_id)
            .fetch()
        )

        return {
            row[0]: MenuItem(
                name=row[0], description=row[1], price=row[2], nutrients=Nutrients.model_validate_json(row[3]) if row[3] else None,
                measure=Measure.model_validate_json(row[4].replace('unit', 'measure_unit')) if row[4] else None, photo=row[5],
                category_name=row[6]
            ) for row in response
        }

    async def __update_menu_items(self, menu_item: MenuItem, menu_item_in_db: MenuItem) -> None:
        update_restaurant = {}

        if menu_item_in_db.description != menu_item.description:
            update_restaurant['description'] = menu_item.description

        if menu_item_in_db.price != menu_item.price:
            update_restaurant['price'] = menu_item.price

        if menu_item.nutrients is not None and menu_item_in_db.nutrients != menu_item.nutrients:
            update_restaurant['nutrients'] = menu_item.nutrients.model_dump_json()

        if menu_item.measure is not None and menu_item_in_db.measure != menu_item.measure:
            update_restaurant['measure'] = menu_item.measure.model_dump_json()

        if menu_item.photo is not None and menu_item_in_db.photo != menu_item.photo:
            update_restaurant['photo'] = menu_item.photo

        if menu_item_in_db.category_name != menu_item.category_name:
            try:
                category_id = await self.__get_category_id(menu_item)
            except ValueError:
                return

            update_restaurant['category_id'] = category_id

        if not update_restaurant:
            return

        await Update(MenuItems).values(update_restaurant).where(MenuItems.name == menu_item.name).execute()

    async def __call__(self, restaurant_id: int, restaurant_slug: str) -> None:
        menu_items = await MenuParser.get_menu(restaurant_slug)

        if not menu_items:
            return

        menu_items_in_db = await self.__get_menu_items_in_db(restaurant_id)

        new_menu_items: list[dict[str, [str, None, datetime]]] = []
        update_menu_items: list[str] = []

        for menu_item in menu_items:
            if (menu_item_in_db := menu_items_in_db.get(menu_item.name, None)) is not None:
                await self.__update_menu_items(menu_item, menu_item_in_db)
                update_menu_items.append(menu_item.name)
                continue

            try:
                category_id = await self.__get_category_id(menu_item)
            except ValueError:
                continue

            new_menu_items.append(
                dict(
                    category_id=category_id,
                    name=menu_item.name,
                    description=menu_item.description,
                    price=menu_item.price,
                    nutrients=menu_item.nutrients.model_dump_json() if menu_item.nutrients else None,
                    measure=menu_item.measure.model_dump_json() if menu_item.measure else None,
                    photo=menu_item.photo,
                    restaurant_id=restaurant_id,
                    last_parsing_time=datetime.now()
                )
            )

        for result in (new_menu_items[n:n + 50] for n in range(0, len(new_menu_items), 50)):
            await Insert(MenuItems).values(result).execute()

        if update_menu_items:
            await (
                Update(MenuItems).values(last_parsing_time=datetime.now())
                .where(MenuItems.name.in_(update_menu_items))
                .execute()
            )


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
