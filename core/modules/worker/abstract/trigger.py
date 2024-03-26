from abc import abstractmethod, ABC

from core.modules.database.methods import Database
from core.modules.worker.abstract.lifespan import Lifespan


class BaseTrigger(Lifespan, ABC):

    async def startup(self) -> None:
        await Database.connect()

    async def shutdown(self) -> None:
        await Database.disconnect()

    @abstractmethod
    async def __call__(self) -> list | None:
        raise NotImplementedError
