import asyncio
from asyncio import sleep

from aiohttp import ClientSession, ClientError, ClientTimeout

from core.modules.api.schemes import Method, Response


class API:
    __session: ClientSession = None

    @classmethod
    async def __request(cls, method: Method, url: str, headers: dict, cookies: dict, depth: int = 0, **kwargs) -> Response:
        if depth == 3:
            return Response(content=None, status_code=500)

        headers, cookies = headers or {}, cookies or {}

        if cls.__session is None:
            cls.__session = ClientSession(timeout=ClientTimeout(total=60))

        try:
            async with cls.__session.request(method, url, headers=headers, cookies=cookies, **kwargs) as resp:
                content, status_code = await resp.read(), resp.status
        except (ClientError, asyncio.TimeoutError):
            return await cls.__request(method, url, headers, cookies, depth + 1, **kwargs)

        return Response(content=content, status_code=status_code)

    @classmethod
    async def post(cls, url: str, *, headers: dict = None, cookies: dict = None, **kwargs) -> Response:
        return await cls.__request('POST', url, headers, cookies, **kwargs)

    @classmethod
    async def get(cls, url: str, *, params: dict = None, headers: dict = None, cookies: dict = None, **kwargs) -> Response:
        return await cls.__request('GET', url, headers, cookies, params=params, **kwargs)

    @classmethod
    async def delete(cls, url: str, *, headers: dict = None, cookies: dict = None, **kwargs) -> Response:
        return await cls.__request('DELETE', url, headers, cookies, **kwargs)

    @classmethod
    async def put(cls, url: str, *, headers: dict = None, cookies: dict = None, **kwargs) -> Response:
        return await cls.__request('PUT', url, headers, cookies, **kwargs)

    @classmethod
    async def disconnect(cls):
        if cls.__session is not None:
            await cls.__session.close()
            await sleep(0)
