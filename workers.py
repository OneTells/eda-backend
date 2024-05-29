from core.general.methods.logger import enable_logger

enable_logger()

if __name__ == '__main__':
    from time import sleep

    from core.modules.worker.methods.worker import WorkerManager
    from modules.parsers.modules.allergens.workers import AllergenParserWorker
    from modules.parsers.modules.menu.workers import MenuItemSearcherWorker
    from modules.parsers.modules.restaurants.workers import RestaurantSearcherWorker

    worker_manager = WorkerManager(
        RestaurantSearcherWorker, MenuItemSearcherWorker, AllergenParserWorker
    )

    worker_manager.start()

    try:
        while True:
            sleep(3600)
    except KeyboardInterrupt:
        pass

    worker_manager.close()
