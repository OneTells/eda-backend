from multiprocessing.context import SpawnProcess

from core.modules.logger.methods import logger
from core.modules.worker.abstract.worker import BaseWorker
from core.modules.worker.methods.trigger import Trigger
from core.modules.worker.schemes.worker import WorkerData


class WorkerProcess:

    def __init__(self, worker: type[BaseWorker]) -> None:
        self.__worker = worker
        self.__process: SpawnProcess | None = None

    def start(self) -> None:
        self.__process = SpawnProcess(
            target=Trigger.run,
            args=(
                WorkerData(
                    worker_name=self.__worker.__name__, setting=self.__worker.setting(),
                    trigger=self.__worker.trigger(), executor=self.__worker.executor()
                ),
            ), name=f'Trigger_{self.__worker.__name__}'
        )
        self.__process.start()

        logger.info(f'{self.__worker.__name__} запушен')

    def terminate(self):
        self.__process.terminate()
        logger.info(f'В {self.__worker.__name__} отправлен запрос о завершении работы')

    def close(self):
        try:
            self.__process.join()
        except KeyboardInterrupt as error:
            logger.error(f'{self.__worker.__name__} ошибка при закрытии')
            raise error

        self.__process.close()

        logger.info(f'{self.__worker.__name__} остановлен')


class WorkerManager:

    def __init__(self, *workers: type[BaseWorker]):
        self.__workers = [WorkerProcess(worker) for worker in workers]

    def start(self):
        for worker in self.__workers:
            worker.start()

        logger.info('WorkerManager запушен')

    def close(self):
        for worker in self.__workers:
            worker.terminate()

        for worker in self.__workers:
            worker.close()

        logger.info('WorkerManager остановлен')
