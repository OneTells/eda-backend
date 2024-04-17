from abc import ABC, abstractmethod

from core.modules.database.modules.pool.methods import DatabasePool
from core.modules.requests.modules.session.methods import SessionPool
from core.modules.worker.abstract.lifespan import Lifespan


class BaseExecutor(Lifespan, ABC):

    async def startup(self) -> None:
        await DatabasePool.connect()

    async def shutdown(self) -> None:
        await SessionPool.close()
        await DatabasePool.disconnect()

    @abstractmethod
    async def __call__(self, *args) -> None:
        raise NotImplementedError
