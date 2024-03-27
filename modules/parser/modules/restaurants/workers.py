from core.modules.worker.abstract.executor import BaseExecutor
from core.modules.worker.abstract.trigger import BaseTrigger
from core.modules.worker.abstract.worker import BaseWorker
from core.modules.worker.schemes.setting import Setting
from core.modules.worker.utils.timer import timer
from modules.parser.modules.restaurants.methods import Parser
from modules.parser.modules.restaurants.schemes import Location


class Executor(BaseExecutor):

    async def __call__(self, location: Location) -> None:
        restaurants = await Parser.get_restaurants(location)


class Trigger(BaseTrigger):

    async def __call__(self) -> list:
        return ['1212', '12121']


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
