from asyncpg import Pool, create_pool

from core.modules.database.core.config import ConnectionData
from core.modules.logger.methods import logger


class DatabasePool:
    __pool: Pool

    @classmethod
    def get_pool(cls) -> Pool:
        return cls.__pool

    @classmethod
    async def connect(cls, *, pool_size: int = 5) -> None:
        cls.__pool = await create_pool(
            ConnectionData.DSN,
            min_size=pool_size,
            max_size=pool_size,
            max_inactive_connection_lifetime=120,
            command_timeout=60
        )

        logger.info('База данных подключена')

    @classmethod
    async def disconnect(cls) -> None:
        await cls.__pool.close()
        logger.info('База данных отключена')
