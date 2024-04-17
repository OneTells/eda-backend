if __name__ == 'api':
    from fastapi import FastAPI

    from general.methods.api import lifespan
    from modules.api.modules.allergens.api import router as allergen_router
    from modules.api.modules.menu.api import router as menu_router
    from modules.api.modules.restaurants.api import router as restaurants_router

    app = FastAPI(lifespan=lifespan)
    app.include_router(allergen_router)
    app.include_router(menu_router)
    app.include_router(restaurants_router)

if __name__ == '__main__':
    import uvicorn

    from core.modules.logger.methods import logger

    logger.info('API запущен')
    uvicorn.run(
        "api:app", workers=2,
        host='91.222.238.209', port=80, timeout_keep_alive=180,
        log_level='info', access_log=False,
        http='httptools', loop='uvloop'
    )
    logger.info('API выключен')
