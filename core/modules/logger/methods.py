import os
import sys
from multiprocessing import current_process
from sys import stderr
from typing import Literal

from loguru import logger as loguru_logger

type Level = Literal['debug', 'info', 'success', 'warning', 'error', 'critical']


class Logger:
    __is_initialized: bool = False

    __PATH = '/root/logs'
    __FORMAT = "<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <y>{level}</> | <w>{extra[user_id]}</> | <c>{message}</>"

    def __init__(self, user_id: int = 'System') -> None:
        self.__logger = loguru_logger.bind(user_id=user_id)
        self.__connect()

    def logging(self, level: Level, message: str) -> None:
        self.__logger.__getattribute__(level)(message)

    @classmethod
    def __get_path(cls) -> str:
        filename = os.path.basename(sys.argv[0].split('.')[0])

        current_process_name = current_process().name
        sub_path = current_process_name

        if filename == 'workers':
            current_process_name_lower = current_process().name.lower()

            if current_process_name_lower.endswith('worker'):
                if current_process_name_lower.startswith('trigger'):
                    name = 'trigger'
                else:
                    name = 'executor'

                sub_path = f'workers/{current_process_name.split('_')[-1].removesuffix("Worker")}/{name}'
        elif filename == 'main':
            if current_process_name.count('SpawnProcess'):
                sub_path = 'main'

        return f'{cls.__PATH}/{filename}/{sub_path}'

    @classmethod
    def __connect(cls) -> None:
        if cls.__is_initialized:
            return

        if not os.path.isdir(path := cls.__get_path()):
            os.makedirs(path)

        cls.__is_initialized = True

        loguru_logger.remove()
        loguru_logger.add(stderr, level="INFO", format=cls.__FORMAT, backtrace=True, diagnose=True)
        loguru_logger.add(
            f'{path}/debug.log', level='DEBUG', format=cls.__FORMAT, backtrace=True, diagnose=True,
            compression='tar.xz', retention='10 days', rotation='100 MB'
        )
        loguru_logger.add(
            f'{path}/info.log', level='INFO', format=cls.__FORMAT, backtrace=True, diagnose=True,
            compression='tar.xz', retention='10 days', rotation='100 MB'
        )

    def debug(self, message: str) -> None:
        self.logging('debug', message)

    def info(self, message: str) -> None:
        self.logging('info', message)

    def success(self, message: str) -> None:
        self.logging('success', message)

    def warning(self, message: str) -> None:
        self.logging('warning', message)

    def error(self, message: str) -> None:
        self.logging('error', message)

    def critical(self, message: str) -> None:
        self.logging('critical', message)

    def exception(self, message: str = '') -> None:
        self.__logger.exception(message)


logger = Logger()
