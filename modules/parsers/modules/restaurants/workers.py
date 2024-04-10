from datetime import datetime

from core.general.models.restaurants import Restaurants, Organizations
from core.general.schemes.restaurant import Location
from core.modules.database.methods import Insert, Select, Update
from core.modules.logger.methods import logger
from core.modules.worker.abstract.executor import BaseExecutor
from core.modules.worker.abstract.trigger import BaseTrigger
from core.modules.worker.abstract.worker import BaseWorker
from core.modules.worker.schemes.setting import Setting
from core.modules.worker.utils.timer import timer
from modules.parsers.modules.restaurants.methods import RestaurantParser
from modules.parsers.modules.restaurants.schemes import Restaurant


class Executor(BaseExecutor):

    @staticmethod
    async def __get_organization_id(restaurant: Restaurant) -> int:
        organization_id: int | None = await (
            Select(Organizations.id)
            .where(Organizations.slug == restaurant.brand.slug)
            .fetch_one(model=lambda x: x[0])
        )

        if organization_id is not None:
            return organization_id

        organization_id = await (
            Insert(Organizations)
            .values(name=restaurant.name, slug=restaurant.brand.slug, photo=restaurant.media.photos[0].uri)
            .returning(Organizations.id, model=lambda x: x[0])
        )

        if organization_id is None:
            logger.error(msg := 'Не удалось добавить организацию')
            raise ValueError(msg)

        return organization_id

    async def __call__(self, location: Location) -> None:
        restaurants = await RestaurantParser.get_restaurants(location)

        if not restaurants:
            return

        response = await Select(Restaurants.id, Restaurants.slug, Restaurants.rating).fetch()
        restaurants_in_db: dict[str, tuple[int, float]] = {slug: (id_, rating) for id_, slug, rating in response}

        new_restaurants: list[dict[str, [str, int, datetime]]] = []

        update_time: list[int] = []
        update_rating: list[tuple[int, float]] = []

        current_time = datetime.now()

        for restaurant in restaurants:
            data = restaurants_in_db.get(restaurant.slug, None)

            if data is not None:
                restaurant_id, rating = data

                if rating != restaurant.rating:
                    update_rating.append((restaurant_id, restaurant.rating))

                update_time.append(restaurant_id)
                continue

            await RestaurantParser.add_additional_data(restaurant)

            try:
                organization_id = await self.__get_organization_id(restaurant)
            except ValueError:
                continue

            new_restaurants.append(
                dict(
                    slug=restaurant.slug,
                    organization_id=organization_id,
                    longitude=restaurant.longitude,
                    latitude=restaurant.latitude,
                    rating=restaurant.rating,
                    last_parsing_time=current_time
                )
            )

        for result_ in (new_restaurants[n:n + 50] for n in range(0, len(new_restaurants), 50)):
            await Insert(Restaurants).values(result_).execute()

        if update_time:
            await (
                Update(Restaurants)
                .values(last_parsing_time=current_time)
                .where(Restaurants.id.in_(update_time))
                .execute()
            )

        for restaurant_id, rating in update_rating:
            await (
                Update(Restaurants)
                .values(rating=rating)
                .where(Restaurants.id == restaurant_id)
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
