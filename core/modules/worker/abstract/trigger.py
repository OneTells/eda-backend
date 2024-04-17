from abc import abstractmethod, ABC

from core.modules.database.modules.pool.methods import DatabasePool
from core.modules.worker.abstract.lifespan import Lifespan


class BaseTrigger(Lifespan, ABC):

    async def startup(self) -> None:
        await DatabasePool.connect()

    async def shutdown(self) -> None:
        await DatabasePool.disconnect()

    @abstractmethod
    async def __call__(self) -> list | None:
        raise NotImplementedError
