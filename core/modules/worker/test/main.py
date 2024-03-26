import multiprocessing
import time

from core.modules.worker.abstract.executor import BaseExecutor
from core.modules.worker.abstract.trigger import BaseTrigger
from core.modules.worker.abstract.worker import BaseWorker
from core.modules.worker.methods.worker import WorkerManager
from core.modules.worker.schemes.setting import Setting


class Executor(BaseExecutor):

    async def __call__(self, name: str) -> None:
        print(121)


class Trigger(BaseTrigger):

    async def __call__(self) -> list:
        return ['1212', '12121']


class TestWorker(BaseWorker):

    @staticmethod
    def setting() -> Setting:
        return Setting(timeout=1, worker_count=1)

    @staticmethod
    def executor() -> type[BaseExecutor]:
        return Executor

    @staticmethod
    def trigger() -> type[BaseTrigger]:
        return Trigger


if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')

    worker_manager = WorkerManager(TestWorker)

    worker_manager.start()

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass

    worker_manager.close()
