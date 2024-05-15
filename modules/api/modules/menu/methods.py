import random
from datetime import timedelta, datetime

from core.general.models.menu import MenuItems, Categories
from core.general.models.restaurants import Restaurants
from core.general.models.user import UserHistory
from core.general.schemes.menu import Nutrients
from core.general.schemes.restaurant import Location
from core.modules.database.modules.requests.methods import Select, Insert
from modules.api.core.methods.distance import get_distance
from modules.api.modules.menu.schemes import Menu, Category, MenuItem, Measure


async def get_random_restaurant_id(radius: int, location: Location) -> int | None:
    restaurants = await (
        Select(Restaurants.id, Restaurants.longitude, Restaurants.latitude)
        .where(Restaurants.last_parsing_time + timedelta(days=3) > datetime.now())
        .fetch()
    )

    while restaurants:
        restaurant = random.choice(restaurants)

        current_distance = get_distance(
            Location(latitude=restaurant['latitude'], longitude=restaurant['longitude']), location
        )

        if current_distance <= radius:
            return restaurant['id']

        restaurants.remove(restaurant)

    return


async def get_menu_by_restaurant_id(user_id: int | None, restaurant_id: int) -> Menu:
    if user_id is not None:
        await (
            Insert(UserHistory)
            .values(user_id=user_id, restaurant_id=restaurant_id)
            .execute()
        )
    
    response = await (
        Select(
            MenuItems.name, MenuItems.description, MenuItems.price, MenuItems.photo,
            MenuItems.measure, MenuItems.nutrients, Categories.name.label('category_name'),
        ).join(Categories, MenuItems.category_id == Categories.id)
        .where(MenuItems.restaurant_id == restaurant_id, MenuItems.last_parsing_time + timedelta(days=3) > datetime.now())
        .fetch()
    )

    categories: dict[str, Category] = {}

    for menu_item_in_db in response:
        menu_item = MenuItem(
            name=menu_item_in_db['name'],
            description=menu_item_in_db['description'],
            price=menu_item_in_db['price'],
            photo=f'https://eda.yandex{menu_item_in_db['photo']}',
            measure=Measure.model_validate_json(menu_item_in_db['measure']) if menu_item_in_db['measure'] else None,
            nutrients=Nutrients.model_validate_json(menu_item_in_db['nutrients']) if menu_item_in_db['nutrients'] else None,
        )

        if (category := categories.get(category_name := menu_item_in_db['category_name'], None)) is None:
            categories[category_name] = Category(name=category_name, menu_items=[menu_item])
        else:
            category.menu_items.append(menu_item)

    return Menu(categories=list(categories.values()))
