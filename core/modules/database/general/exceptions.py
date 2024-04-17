from core.modules.logger.methods import logger


class DatabaseError(Exception):

    def __init__(self, compiled_query: str) -> None:
        self.__message = f'DatabaseError: Слишком много попыток выполнить запрос. Запрос: {compiled_query}'
        logger.error(self.__message)

    def __str__(self) -> str:
        return self.__message


class FetchOneError(DatabaseError):

    def __init__(self, compiled_query: str) -> None:
        self.__message = f'FetchOneError: Запрос вернул несколько записей. Запрос: {compiled_query}'
        logger.error(self.__message)
