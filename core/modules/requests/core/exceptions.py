from core.modules.requests.core.schemes import Response
from core.modules.logger.methods import logger


class GetFileError(Exception):

    def __init__(self, message: str, url: str, response: Response) -> None:
        self.raw_message = message
        self.url = url
        self.response = response

        self.message = f'GetFileError: {message}. Ссылка: {url}, Ответ сервера:  {response}'
        logger.error(self.message)

    def __str__(self) -> str:
        return self.message
