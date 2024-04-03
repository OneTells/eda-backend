import asyncio

from core.general.models.restaurants import Restaurants, Organizations
from core.general.utils.counter import TimeCounter
from core.modules.database.methods import Insert, Select
from core.modules.worker.abstract.executor import BaseExecutor
from core.modules.worker.abstract.trigger import BaseTrigger
from core.modules.worker.abstract.worker import BaseWorker
from core.modules.worker.schemes.setting import Setting
from core.modules.worker.utils.timer import timer
from modules.parser.modules.restaurants.methods import Parser
from modules.parser.modules.restaurants.schemes import Location, Restaurant


class Executor(BaseExecutor):
    __time_counter = TimeCounter(minutes=1)

    @classmethod
    async def __flood_control(cls):
        if cls.__time_counter.add() >= 20:
            await asyncio.sleep(cls.__time_counter.time_until_element_is_deleted)

    @staticmethod
    async def __get_organization_id(restaurant: Restaurant) -> int:
        organization_id: int | None = await (
            Select(Organizations.id)
            .where(Organizations.slug == restaurant.brand.slug)
            .fetch_one(model=lambda x: x[0])
        )

        if organization_id is None:
            organization_id = await (
                Insert(Organizations)
                .values(name=restaurant.name, slug=restaurant.brand.slug, photo=restaurant.media.photos[0].uri)
                .on_conflict_do_nothing()
                .returning(Organizations.id, model=lambda x: x[0])
            )

        return organization_id

    async def __call__(self, location: Location) -> None:
        await self.__flood_control()

        restaurants = await Parser.get_restaurants(location)

        if not restaurants:
            return

        result = []

        for restaurant in restaurants:
            organization_id = await self.__get_organization_id(restaurant)
            result.append(dict(slug=restaurant.slug, organization_id=organization_id))

        await (
            Insert(Restaurants)
            .values(result)
            .on_conflict_do_nothing()
            .execute()
        )


class Trigger(BaseTrigger):
    LATITUDE_MIN = 56.745
    LATITUDE_MAX = 56.920
    LATITUDE_STEP = 0.005

    LONGITUDE_MIN = 60.400
    LONGITUDE_MAX = 60.830
    LONGITUDE_STEP = 0.005

    async def __call__(self) -> list[Location]:
        result = []

        latitude = self.LATITUDE_MIN

        while latitude <= self.LATITUDE_MAX:
            longitude = self.LATITUDE_MIN

            while longitude <= self.LONGITUDE_MAX:
                result.append(
                    Location(
                        latitude=latitude,
                        longitude=longitude
                    )
                )

                longitude += self.LONGITUDE_STEP

            latitude += self.LATITUDE_STEP

        return result


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
