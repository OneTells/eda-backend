import random
from datetime import timedelta, datetime

from core.general.models.allergen import AllergenMatches
from core.general.models.menu import MenuItemAllergens
from core.general.models.menu import MenuItems, Categories
from core.general.models.restaurants import Restaurants
from core.general.models.user import UserHistory, UserAllergen, UserSetting
from core.general.schemes.menu import Nutrients
from core.general.schemes.restaurant import Location
from core.modules.database.methods.requests import Select, Insert
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

        category_count: int | None = await (
            Select(UserSetting.value)
            .where(UserSetting.user_id == user_id, UserSetting.setting_id == 1)
            .fetch_one(model=lambda x: int(x[0]))
        )

        category_ids = await (
            Select(MenuItems.category_id.distinct())
            .where(MenuItems.restaurant_id == restaurant_id)
            .fetch(model=lambda x: x[0])
        )

        selected_category_ids = random.sample(category_ids, category_count or 5)

        response = await (
            Select(
                MenuItems.name, MenuItems.description, MenuItems.price, MenuItems.photo,
                MenuItems.measure, MenuItems.nutrients, Categories.name.label('category_name'),
            ).join(Categories, MenuItems.category_id == Categories.id)
            .where(
                MenuItems.restaurant_id == restaurant_id,
                MenuItems.last_parsing_time + timedelta(days=3) > datetime.now(),
                ~Select(1)
                .select_from(MenuItemAllergens)
                .join(AllergenMatches, MenuItemAllergens.allergen_match_id == AllergenMatches.id)
                .where(
                    AllergenMatches.allergen_id
                    .in_(
                        Select(UserAllergen.allergen_id)
                        .where(UserAllergen.user_id == user_id, UserAllergen.is_selected)
                        .scalar_subquery()
                    ),
                    AllergenMatches.percent >= 70,
                    MenuItemAllergens.menu_item_id == MenuItems.id
                )
                .exists(),
                Categories.id.in_(selected_category_ids)
            ).fetch()
        )
    else:
        category_count = 5

        category_ids = await (
            Select(MenuItems.category_id.distinct())
            .where(MenuItems.restaurant_id == restaurant_id)
            .fetch(model=lambda x: x[0])
        )

        selected_category_ids = random.sample(category_ids, category_count)

        response = await (
            Select(
                MenuItems.name, MenuItems.description, MenuItems.price, MenuItems.photo,
                MenuItems.measure, MenuItems.nutrients, Categories.name.label('category_name'),
            ).where(
                MenuItems.restaurant_id == restaurant_id,
                MenuItems.last_parsing_time + timedelta(days=3) > datetime.now(),
                Categories.id.in_(selected_category_ids)
            ).fetch()
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

    if user_id is not None:
        menu_item_count = await (
            Select(UserSetting.value)
            .where(UserSetting.user_id == user_id, UserSetting.setting_id == 2)
            .fetch_one(model=lambda x: int(x[0]))
        )
    else:
        menu_item_count = 5

    for category in categories.values():
        category.menu_items = random.sample(category.menu_items, menu_item_count or 5)

    return Menu(categories=list(categories.values()))
