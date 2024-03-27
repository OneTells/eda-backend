from core.general.models.restaurants import Restaurants, Organizations
from core.modules.database.methods import Insert, Select
from core.modules.worker.abstract.executor import BaseExecutor
from core.modules.worker.abstract.trigger import BaseTrigger
from core.modules.worker.abstract.worker import BaseWorker
from core.modules.worker.schemes.setting import Setting
from core.modules.worker.utils.timer import timer
from modules.parser.modules.restaurants.methods import Parser
from modules.parser.modules.restaurants.schemes import Location, Restaurant


class Executor(BaseExecutor):

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
        restaurants = await Parser.get_restaurants(location)
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

    async def __call__(self) -> list[Location]:
        return [
            Location(
                latitude=56.838010,
                longitude=60.597465
            )
        ]


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
