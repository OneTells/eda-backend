from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.general.config.database import database_data
from core.general.methods.logger import enable_logger
from core.modules.database.methods.pool import DatabasePool
from core.modules.logger.methods import logger
from core.modules.requests.methods.sessions import SessionPool


async def on_startup():
    enable_logger()

    logger.info('Worker запушен')
    await DatabasePool.connect(database_data, pool_size=3)


async def on_shutdown():
    logger.info('Worker остановлен')

    await DatabasePool.disconnect()
    await SessionPool.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await on_startup()
    yield
    await on_shutdown()
