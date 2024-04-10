if __name__ == 'main':
    from fastapi import FastAPI

    from modules.api.core.methods import lifespan
    from modules.api.modules.allergens.api import router as allergen_router

    app = FastAPI(lifespan=lifespan)
    app.include_router(allergen_router)

if __name__ == '__main__':
    import uvicorn

    from core.modules.logger.methods import logger

    logger.info('API запущен')
    uvicorn.run(
        "main:app", workers=2,
        host='91.222.238.209', port=80, timeout_keep_alive=180,
        log_level='info', access_log=False,
        http='httptools', loop='uvloop'
    )
    logger.info('API выключен')
