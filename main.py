if __name__ == 'main':
    from logging import basicConfig, DEBUG
    from sys import stdout

    from modules.api.general.objects.api import app

    from modules.api.modules.allergens.api import router as allergen_router

    app.include_router(allergen_router)

    basicConfig(level=DEBUG, stream=stdout)

if __name__ == '__main__':
    import asyncio
    import uvicorn
    import uvloop

    from core.general.config import ServerInfo
    from core.modules.logger.methods import logger


    async def main():
        logger.info('API запущен')
        uvicorn.run(
            "main:app", host=ServerInfo.IP, port=ServerInfo.PORT, workers=2,
            log_level='info', access_log=False, http='httptools', timeout_keep_alive=180, loop='uvloop'
        )
        logger.info('API выключен')
        await asyncio.sleep(0)


    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        runner.run(main())
