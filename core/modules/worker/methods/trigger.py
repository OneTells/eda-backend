import asyncio
import time
from array import ArrayType
from asyncio import sleep, CancelledError
from multiprocessing import Queue, Array
from signal import signal, SIGTERM, SIGINT, SIG_IGN, default_int_handler

import uvloop
from _queue import Empty

from core.general.models.workers import Workers
from core.modules.database.methods import Select, Insert
from core.modules.logger.methods import logger
from core.modules.worker.exceptions.trigger import ReloadTriggerError
from core.modules.worker.methods.executor import ExecutorProcess
from core.modules.worker.schemes.executor import ExecutorProcessData
from core.modules.worker.schemes.worker import WorkerData


class Trigger:

    def __init__(self, worker_data: WorkerData):
        self.__worker_data = worker_data
        self.__trigger = self.__worker_data.trigger()

        self.__executors: list[ExecutorProcess] = []

        self.__queue: Queue | None = None
        self.__limited_args_queue: Queue | None = None

    def __create_limited_args(self) -> tuple[list[tuple], ArrayType, Queue] | None:
        if self.__worker_data.setting.limited_args is None:
            return

        self.__limited_args_queue = Queue()

        limited_args = self.__worker_data.setting.limited_args.unpack()

        limited_args_list = []
        limited_args_array: ArrayType = Array('i', len(limited_args))

        for index, arg in enumerate(limited_args):
            limited_args_list.append(arg)
            limited_args_array[index] = -1

            self.__limited_args_queue.put(index)

        return limited_args_list, limited_args_array, self.__limited_args_queue

    async def __startup(self) -> None:
        await self.__trigger.startup()

        if not self.__worker_data.setting.worker_count or self.__worker_data.executor is None:
            return

        self.__queue = Queue()
        limited_args = self.__create_limited_args()

        for number in range(self.__worker_data.setting.worker_count):
            self.__executors.append(
                executor := ExecutorProcess(
                    ExecutorProcessData(
                        number=number, limited_args=limited_args, queue=self.__queue, worker_data=self.__worker_data
                    )
                )
            )
            executor.start()

    async def __sleep(self, timeout: float) -> None:
        start_time = time.time()

        while True:
            if not any(executor.is_alive() for executor in self.__executors):
                break

            if time.time() - start_time >= timeout:
                break

            await sleep(0.5)

    async def __shutdown(self) -> None:
        await self.__trigger.shutdown()

        if not self.__worker_data.setting.worker_count:
            logger.info(f'{self.__worker_data.worker_name} триггер завершён')
            return

        while not self.__queue.empty():
            try:
                self.__queue.get(block=False)
            except Empty:
                break

        for _ in range(self.__worker_data.setting.worker_count):
            self.__queue.put('Stop')

        await self.__sleep(80)

        for executor in self.__executors:
            executor.terminate()

        await self.__sleep(10)

        for executor in self.__executors:
            executor.close()

        self.__queue.close()

        if self.__limited_args_queue is not None:
            self.__limited_args_queue.close()

        self.__executors.clear()

        logger.info(f'{self.__worker_data.worker_name} триггер завершён')

    async def __is_on(self) -> bool:
        try:
            is_trigger_on: bool | None = await (
                Select(Workers.is_trigger_on)
                .where(Workers.name == self.__worker_data.worker_name)
                .fetch_one(model=lambda x: x[0])
            )

            if is_trigger_on is None:
                await Insert(Workers).values(name=self.__worker_data.worker_name, is_trigger_on=False).execute()
                return False
        except Exception as error:
            logger.exception(str(error))
            logger.error(f'Ошибка в проверке работы {self.__worker_data.worker_name} trigger')
            return False

        return is_trigger_on is True

    async def __wait_end_work_executors(self) -> None:
        while True:
            is_work = False
            is_reset = False

            for executor in self.__executors:
                if self.__queue.empty() and not executor.is_working:
                    continue

                if time.time() - executor.time() > self.__worker_data.setting.timeout_reset:
                    is_reset = True
                else:
                    is_reset = False

                is_work = True

            if is_reset:
                raise ReloadTriggerError()

            if not is_work:
                break

            await sleep(1)

    async def __run_trigger(self) -> bool:
        try:
            result = await self.__trigger()
        except Exception as error:
            _ = error

            logger.exception()
            logger.error(f'Ошибка при выполнении {self.__worker_data.worker_name} trigger')
            return False

        for obj in (result or []):
            self.__queue.put(obj)

        return True

    async def __run(self):
        while True:
            if not await self.__is_on():
                await sleep(30)
                continue

            if not await self.__run_trigger():
                continue

            await sleep(self.__worker_data.setting.timeout)
            await self.__wait_end_work_executors()

    async def __run_with_reloader(self) -> None:
        is_reload = False

        while True:
            await self.__startup()
            logger.info(f'{self.__worker_data.worker_name} триггер запушен')

            if is_reload:
                logger.warning(f'{self.__worker_data.worker_name} перезагружен')
            else:
                is_reload = True

            try:
                await self.__run()
            except ReloadTriggerError:
                logger.warning(f'{self.__worker_data.worker_name} завис, выполняется перезагрузка')

                await self.__shutdown()
                continue
            except CancelledError:
                logger.info(f'{self.__worker_data.worker_name} триггер принял запрос о завершении работы')

            await self.__shutdown()
            return

    @classmethod
    def run(cls, worker_data: WorkerData) -> None:
        signal(SIGINT, SIG_IGN)
        signal(SIGTERM, default_int_handler)

        try:
            with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
                runner.run(cls(worker_data).__run_with_reloader())
        except KeyboardInterrupt:
            pass
