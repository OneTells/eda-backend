from core.general.config.database import database_data
from core.modules.database.methods.pool import DatabasePool
from core.modules.requests.methods.sessions import SessionPool
from core.modules.worker.abstract.lifespan import Lifespan as Lifespan_


class Lifespan(Lifespan_):

    async def startup(self) -> None:
        await DatabasePool.connect(database_data)

    async def shutdown(self) -> None:
        await DatabasePool.disconnect()
        await SessionPool.close()
