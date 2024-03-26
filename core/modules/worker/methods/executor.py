import asyncio
import time
from asyncio import CancelledError
from multiprocessing import Event, Value
from multiprocessing.context import SpawnProcess
from multiprocessing.managers import ValueProxy
from signal import signal, SIGTERM, SIGINT, SIG_IGN, default_int_handler
from typing import Any, AsyncIterator

import uvloop

from core.modules.logger.methods import logger
from core.modules.worker.schemes.executor import ExecutorData, ExecutorProcessData


class Executor:

    def __init__(self, executor_data: ExecutorData):
        self.__executor_data = executor_data
        self.__executor = executor_data.executor()

        self.__lifespan: AsyncIterator | None = None

    async def __startup(self) -> None:
        await self.__executor.startup()

    async def __shutdown(self) -> None:
        await self.__executor.shutdown()

    def __get_final_args(self, args: Any) -> tuple[int | None, tuple]:
        if not isinstance(args, tuple):
            args = (args,)

        if self.__executor_data.limited_args is None:
            return None, args

        index = self.__executor_data.limited_args[2].get()
        unused_arg = self.__executor_data.limited_args[0][index]

        self.__executor_data.limited_args[1][index] = self.__executor_data.number

        return index, args + unused_arg

    async def __run(self):
        await self.__startup()
        logger.info(f'{self.__executor_data.worker_name} исполнитель запушен')

        try:
            while True:
                if (args_in_queue := self.__executor_data.queue.get()) == 'Stop':
                    break

                index, args = self.__get_final_args(args_in_queue)

                self.__executor_data.set_start_work()

                logger.debug(f'{self.__executor_data.worker_name} executor {args}')

                try:
                    await self.__executor(*args)
                except Exception as error:
                    _ = error

                    logger.exception()
                    logger.error(f'Ошибка при выполнении {self.__executor_data.worker_name} исполнителя {args}')

                self.__executor_data.set_finish_work()

                if index is not None:
                    self.__executor_data.limited_args[1][index] = -1
                    self.__executor_data.limited_args[2].put(index)

                del args, args_in_queue, index
        except CancelledError:
            logger.info(f'{self.__executor_data.worker_name} исполнитель принял запрос о завершении работы')

        await self.__shutdown()
        logger.info(f'{self.__executor_data.worker_name} исполнитель завершён')

    @classmethod
    def run(cls, executor_data: ExecutorData) -> None:
        signal(SIGINT, SIG_IGN)
        signal(SIGTERM, default_int_handler)

        try:
            with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
                runner.run(cls(executor_data).__run())
        except KeyboardInterrupt:
            pass


class ExecutorProcess:

    def __init__(self, data: ExecutorProcessData) -> None:
        self.__data = data

        self.__is_run_worker: Event | None = None
        self.__counter: ValueProxy[int] | None = None

        self.__process: SpawnProcess | None = None

        self.__current_time: float | None = None
        self.__current_counter: int | None = None

    def time(self):
        if self.__current_counter != self.__counter.value:
            self.__current_time = time.time()
            self.__current_counter = self.__counter.value

        return self.__current_time

    @property
    def is_working(self):
        return self.__is_run_worker.is_set()

    def start(self):
        self.__is_run_worker = Event()
        self.__counter = Value('l', 0)

        self.__process = SpawnProcess(
            target=Executor.run,
            args=(
                ExecutorData(
                    queue=self.__data.queue, is_run_worker=self.__is_run_worker,
                    worker_name=self.__data.worker_data.worker_name,
                    counter=self.__counter, limited_args=self.__data.limited_args,
                    executor=self.__data.worker_data.executor, number=self.__data.number
                ),
            ),
            name=f'Executor_{self.__data.number}_{self.__data.worker_data.worker_name}'
        )

        self.__process.start()

        self.__current_time = None
        self.__current_counter = None

    def is_alive(self) -> bool:
        return self.__process.is_alive()

    def terminate(self):
        self.__process.terminate()

    def close(self):
        self.__process.join()
        self.__process.close()
