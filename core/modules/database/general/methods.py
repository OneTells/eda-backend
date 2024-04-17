from asyncio import sleep
from inspect import isclass
from typing import Callable

from asyncpg import Record, ConnectionDoesNotExistError, CannotConnectNowError, Connection
from pydantic import BaseModel

from core.modules.database.core.schemes import Query, T, Result
from core.modules.database.general.exceptions import DatabaseError, FetchOneError
from core.modules.database.modules.compiler.methods import Compiler
from core.modules.database.modules.pool.methods import DatabasePool


class Database:

    @classmethod
    async def __fetch(cls, compiled_query: str, connection: Connection = None, depth: int = 0) -> list[Record]:
        try:
            return await (connection or DatabasePool.get_pool()).fetch(compiled_query)
        except (CannotConnectNowError, ConnectionDoesNotExistError, ConnectionRefusedError) as error:
            if depth == 3:
                raise DatabaseError(compiled_query) from error

            await sleep(3)
            return await cls.__fetch(compiled_query, connection, depth + 1)

    @classmethod
    async def __execute(cls, compiled_query: str, connection: Connection = None, depth: int = 0) -> None:
        try:
            await (connection or DatabasePool.get_pool()).execute(compiled_query)
        except (CannotConnectNowError, ConnectionDoesNotExistError, ConnectionRefusedError) as error:
            if depth == 3:
                raise DatabaseError(compiled_query) from error

            await sleep(3)
            return await cls.__execute(compiled_query, connection, depth + 1)

    @classmethod
    async def fetch(cls, query: Query, *, model: type[T] | Callable[[Record], Result] = None, connection: Connection = None) -> list[Record | Result | T]:
        result = await cls.__fetch(Compiler.compile_query(query), connection)

        if model is None:
            return result

        if isclass(model) and issubclass(model, BaseModel):
            return list(map(lambda record: model(**record), result))

        return list(map(model, result))

    @classmethod
    async def fetch_one(cls, query: Query, *, model: type[T] | Callable[[Record], Result] = None, connection: Connection = None) -> Record | Result | T | None:
        result = await cls.__fetch(compiled_query := Compiler.compile_query(query), connection)

        if len(result) == 0:
            return None

        if len(result) > 1:
            raise FetchOneError(compiled_query)

        if model is None:
            return result[0]

        if isclass(model) and issubclass(model, BaseModel):
            return model(**result[0])

        return model(result[0])

    @classmethod
    async def execute(cls, query: Query, connection: Connection = None) -> None:
        await cls.__execute(Compiler.compile_query(query), connection)
