import asyncio
from asyncio import sleep
from io import BytesIO
from typing import Self, Any

from aiohttp import ClientError
from aiohttp.client import ClientSession

from core.modules.requests.core.config import DEFAULT_HEADERS
from core.modules.requests.core.exceptions import GetFileError
from core.modules.requests.core.schemes import Response, Methods, RequestArgs, Dict, Params


class Session:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        SessionPool.add(instance)
        return instance

    def __init__(self, **kwargs):
        self.__session = ClientSession(**kwargs)

    async def __request(self, method: Methods, url: str, depth: int = 0, **kwargs: Any) -> Response:
        try:
            async with self.__session.request(method, url, **kwargs) as response:
                return Response(content=await response.read(), status_code=response.status, row_response=response)
        except (ClientError, asyncio.TimeoutError):
            if depth == 2:
                return Response(content=None, status_code=500, row_response=None)

            return await self.__request(method, url, depth + 1, **kwargs)

    async def request(self, method: Methods, url: str, **kwargs) -> Response:
        args = RequestArgs(**kwargs)

        args.headers = args.headers or DEFAULT_HEADERS
        args.cookies = args.cookies or {}

        return await self.__request(method, url, **args.model_dump(by_alias=True))

    async def close(self) -> None:
        await self.__session.close()
        SessionPool.remove(self)

    async def get(self, url: str, *, params: Params = None, headers: Dict = None, cookies: Dict = None, **kwargs) -> Response:
        return await self.request('GET', url, params=params, headers=headers, cookies=cookies, **kwargs)

    async def post(self, url: str, *, headers: Dict = None, cookies: Dict = None, **kwargs) -> Response:
        return await self.request('POST', url, headers=headers, cookies=cookies, **kwargs)

    async def put(self, url: str, *, headers: Dict = None, cookies: Dict = None, **kwargs) -> Response:
        return await self.request('PUT', url, headers=headers, cookies=cookies, **kwargs)

    async def delete(self, url: str, *, headers: Dict = None, cookies: Dict = None, **kwargs) -> Response:
        return await self.request('DELETE', url, headers=headers, cookies=cookies, **kwargs)

    async def get_file(self, url: str) -> BytesIO:
        response = await self.get(url)

        if response.status_code == 200:
            return BytesIO(response.content)

        if response.status_code in (500, 502, 503):
            raise GetFileError('Нет доступа к файлу', url, response)

        raise GetFileError('Неизвестная ошибка при получении файла', url, response)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_) -> None:
        await self.close()


class SessionPool:
    __sessions: list[Session] = []

    @classmethod
    def add(cls, element: Session):
        cls.__sessions.append(element)

    @classmethod
    def remove(cls, element: Session):
        cls.__sessions.remove(element)

    @classmethod
    async def close(cls):
        for session in cls.__sessions.copy():
            await session.close()

        await sleep(0)
