from core.modules.logger.methods import logger


class CompilationError(Exception):

    def __init__(self, query: str) -> None:
        self.__message = f'CompilationError: При компиляции произошла ошибка. Объект компиляции: {query}'
        logger.error(self.__message)

    def __str__(self) -> str:
        return self.__message
