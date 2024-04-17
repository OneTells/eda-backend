from datetime import timedelta, datetime

from core.general.models.menu import MenuItems, Categories
from core.general.schemes.menu import Nutrients
from core.modules.database.modules.requests.methods import Select
from modules.api.modules.menu.schemes import Menu, Category, MenuItem, Measure


async def get_menu_by_restaurant_id(restaurant_id: int) -> Menu:
    response = await (
        Select(
            MenuItems.name, MenuItems.description, MenuItems.price, MenuItems.photo,
            MenuItems.measure, MenuItems.nutrients, Categories.name.label('category_name'),
        ).join(Categories, MenuItems.category_id == Categories.id)
        .where(MenuItems.restaurant_id == restaurant_id)
        .fetch()
    )
    # , MenuItems.last_parsing_time + timedelta(days=3) > datetime.now()
    categories: dict[str, Category] = {}

    for menu_item_in_db in response:
        menu_item = MenuItem(
            name=menu_item_in_db['name'],
            description=menu_item_in_db['description'],
            price=menu_item_in_db['price'],
            photo=menu_item_in_db['photo'],
            measure=Measure.model_validate_json(menu_item_in_db['measure']) if menu_item_in_db['measure'] else None,
            nutrients=Nutrients.model_validate_json(menu_item_in_db['nutrients']) if menu_item_in_db['nutrients'] else None,
        )

        if (category := categories.get(category_name := menu_item_in_db['category_name'], None)) is None:
            categories[category_name] = Category(name=category_name, menu_items=[menu_item])
        else:
            category.menu_items.append(menu_item)

    return Menu(categories=list(categories.values()))
