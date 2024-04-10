from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.modules.database.methods import Database
from core.modules.logger.methods import logger
from core.modules.requests.modules.session.methods import SessionPool


async def on_startup():
    logger.info('Worker запушен')
    await Database.connect(pool_size=3)


async def on_shutdown():
    logger.info('Worker остановлен')

    await Database.disconnect()
    await SessionPool.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await on_startup()
    yield
    await on_shutdown()
