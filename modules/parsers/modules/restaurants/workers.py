from datetime import datetime

from core.general.models.restaurants import Restaurants, Organizations
from core.general.schemes.restaurant import Location
from core.modules.database.modules.requests.methods import Select, Insert, Update
from core.modules.logger.methods import logger
from core.modules.worker.abstract.executor import BaseExecutor
from core.modules.worker.abstract.trigger import BaseTrigger
from core.modules.worker.abstract.worker import BaseWorker
from core.modules.worker.schemes.setting import Setting
from core.modules.worker.utils.timer import timer
from modules.parsers.modules.restaurants.methods import RestaurantParser
from modules.parsers.modules.restaurants.schemes import Restaurant, Organization


class Executor(BaseExecutor):

    @staticmethod
    async def __get_organization_id(restaurant: Restaurant) -> int:
        organization_id: int | None = await (
            Select(Organizations.id)
            .where(Organizations.slug == restaurant.organization.slug)
            .fetch_one(model=lambda x: x[0])
        )

        if organization_id is not None:
            return organization_id

        organization_id = await (
            Insert(Organizations)
            .values(restaurant.organization.model_dump())
            .returning(Organizations.id, model=lambda x: x[0])
        )

        if organization_id is None:
            logger.error(msg := 'Не удалось добавить организацию')
            raise ValueError(msg)

        return organization_id

    @staticmethod
    async def __get_restaurants_in_db() -> dict[str, Restaurant]:
        response = await (
            Select(
                Restaurants.slug, Restaurants.rating, Restaurants.longitude, Restaurants.latitude,
                Organizations.slug, Organizations.name, Organizations.photo
            ).join(Organizations, Restaurants.organization_id == Organizations.id)
            .fetch()
        )

        return {
            row[0]: Restaurant(
                slug=row[0], organization=Organization(slug=row[4], name=row[6], photo=row[6]),
                rating=row[1], longitude=row[2], latitude=row[3]
            ) for row in response
        }

    async def __update_restaurant(self, restaurant: Restaurant, restaurant_in_db: Restaurant) -> None:
        update_restaurant = {}

        if restaurant_in_db.rating != restaurant.rating:
            update_restaurant['rating'] = restaurant.rating

        if restaurant_in_db.longitude != restaurant.longitude:
            update_restaurant['longitude'] = restaurant.longitude

        if restaurant_in_db.latitude != restaurant.latitude:
            update_restaurant['latitude'] = restaurant.latitude

        if restaurant_in_db.organization.slug != restaurant.organization.slug:
            try:
                organization_id = await self.__get_organization_id(restaurant)
            except ValueError:
                return

            update_restaurant['organization_id'] = organization_id
        else:
            update_organization = {}

            if restaurant_in_db.organization.name != restaurant.organization.name:
                update_organization['name'] = restaurant.organization.name

            if restaurant.organization.photo is not None and restaurant_in_db.organization.photo != restaurant.organization.photo:
                update_organization['photo'] = restaurant.organization.photo

            if update_organization:
                await (
                    Update(Organizations)
                    .values(update_organization)
                    .where(Organizations.slug == restaurant.organization.slug)
                    .execute()
                )

        if not update_restaurant:
            return

        await Update(Restaurants).values(update_restaurant).where(Restaurants.slug == restaurant.slug).execute()

    async def __call__(self, location: Location) -> None:
        restaurants = await RestaurantParser.get_restaurants(location)

        if not restaurants:
            return

        restaurants_in_db = await self.__get_restaurants_in_db()

        new_restaurants: list[dict[str, str | int | float | datetime]] = []
        update_restaurants: list[str] = []

        for restaurant in restaurants:
            if (restaurant_in_db := restaurants_in_db.get(restaurant.slug, None)) is not None:
                await self.__update_restaurant(restaurant, restaurant_in_db)
                update_restaurants.append(restaurant.slug)
                continue

            try:
                organization_id = await self.__get_organization_id(restaurant)
            except ValueError:
                continue

            new_restaurants.append(
                dict(
                    slug=restaurant.slug, organization_id=organization_id, longitude=restaurant.longitude,
                    latitude=restaurant.latitude, rating=restaurant.rating, last_parsing_time=datetime.now()
                )
            )

        for result in (new_restaurants[n:n + 50] for n in range(0, len(new_restaurants), 50)):
            await Insert(Restaurants).values(result).execute()

        if update_restaurants:
            await (
                Update(Restaurants).values(last_parsing_time=datetime.now())
                .where(Restaurants.slug.in_(update_restaurants))
                .execute()
            )


class Trigger(BaseTrigger):
    LATITUDE_MIN = 56.745
    LATITUDE_MAX = 56.920
    LATITUDE_STEP = 0.005

    LONGITUDE_MIN = 60.400
    LONGITUDE_MAX = 60.830
    LONGITUDE_STEP = 0.005

    __result: list[Location] | None = None

    async def __call__(self) -> list[Location]:
        if self.__result is not None:
            return self.__result

        self.__result = []

        latitude = self.LATITUDE_MIN

        while latitude <= self.LATITUDE_MAX:
            longitude = self.LATITUDE_MIN

            while longitude <= self.LONGITUDE_MAX:
                self.__result.append(
                    Location(latitude=round(float(latitude), 3), longitude=round(float(longitude), 3))
                )
                longitude += self.LONGITUDE_STEP

            latitude += self.LATITUDE_STEP

        return self.__result


class RestaurantSearcherWorker(BaseWorker):

    @staticmethod
    def setting() -> Setting:
        return Setting(timeout=timer(hours=1), worker_count=1)

    @staticmethod
    def executor() -> type[BaseExecutor]:
        return Executor

    @staticmethod
    def trigger() -> type[BaseTrigger]:
        return Trigger
