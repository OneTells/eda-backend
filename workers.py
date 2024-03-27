if __name__ == '__main__':
    import multiprocessing
    from time import sleep

    from core.modules.worker.methods.worker import WorkerManager
    from modules.parser.modules.restaurants.workers import RestaurantSearcherWorker

    multiprocessing.set_start_method('spawn')

    worker_manager = WorkerManager(RestaurantSearcherWorker)

    worker_manager.start()

    try:
        while True:
            sleep(3600)
    except KeyboardInterrupt:
        pass

    worker_manager.close()
