from abc import ABC, abstractmethod

from core.modules.api.methods import API
from core.modules.database.methods import Database
from core.modules.worker.abstract.lifespan import Lifespan


class BaseExecutor(Lifespan, ABC):

    async def startup(self) -> None:
        await Database.connect()

    async def shutdown(self) -> None:
        await API.disconnect()
        await Database.disconnect()

    @abstractmethod
    async def __call__(self, *args) -> None:
        raise NotImplementedError
