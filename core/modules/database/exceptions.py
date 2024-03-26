from core.modules.logger.methods import logger


class CompilationError(Exception):

    def __init__(self, query: str):
        self.__message = f'CompilationError: При компиляции запроса произошла ошибка. Объект компиляции: {query}'
        logger.error(self.__message)

    def __str__(self):
        return self.__message
