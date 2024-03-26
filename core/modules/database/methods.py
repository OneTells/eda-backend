from asyncio import sleep
from inspect import isclass
from typing import Any, Callable, overload, TypeVar

from asyncpg import Pool, create_pool, Record, ConnectionDoesNotExistError, CannotConnectNowError
from pydantic import BaseModel
from sqlalchemy import Update as Update_, Select as Select_, Delete as Delete_
from sqlalchemy.dialects.postgresql import Insert as _Insert, dialect
from sqlalchemy.exc import CompileError
from sqlalchemy.sql._typing import _ColumnsClauseArgument as Columns
from sqlalchemy.sql.ddl import CreateTable
from sqlalchemy.sql.dml import ReturningInsert

from core.general.models.base import Base
from core.modules.database.config import ConnectionData
from core.modules.database.exceptions import CompilationError
from core.modules.logger.methods import logger

T = TypeVar('T', bound=BaseModel)
FunctionResult = TypeVar('FunctionResult')

Query = Select_ | Update_ | _Insert | Delete_ | ReturningInsert
Model = type[T] | Callable[[Record], FunctionResult] | None


class Select(Select_):

    @overload
    async def fetch(self, *, model: Callable[[Record], FunctionResult]) -> list[FunctionResult]:
        ...

    @overload
    async def fetch(self, *, model: type[T]) -> list[T]:
        ...

    @overload
    async def fetch(self, *, model: None = None) -> list[Record]:
        ...

    async def fetch(self, *, model: Model = None) -> list[Record | FunctionResult | T]:
        return await Database.fetch(self, model=model)

    @overload
    async def fetch_one(self, *, model: type[T]) -> T | None:
        ...

    @overload
    async def fetch_one(self, *, model: Callable[[Record], FunctionResult]) -> FunctionResult | None:
        ...

    @overload
    async def fetch_one(self, *, model: None = None) -> Record | None:
        ...

    async def fetch_one(self, *, model: Model = None) -> Record | FunctionResult | T | None:
        return await Database.fetch_one(self, model=model)


class Update(Update_):

    async def execute(self) -> None:
        await Database.execute(self)


class Insert(_Insert):

    async def execute(self) -> None:
        await Database.execute(self)

    @overload
    async def returning(self, *cols: Columns[Any], model: Callable[[Record], FunctionResult]) -> FunctionResult | None:
        ...

    @overload
    async def returning(self, *cols: Columns[Any], model: type[T]) -> T | None:
        ...

    @overload
    async def returning(self, *cols: Columns[Any], model: None = None) -> Record | None:
        ...

    async def returning(self, *cols: Columns[Any], model: Model = None) -> Record | FunctionResult | T | None:
        return await Database.fetch_one(super().returning(*cols), model=model)


class Delete(Delete_):

    async def execute(self) -> None:
        await Database.execute(self)


class Database:
    __pool: Pool

    @classmethod
    async def connect(cls, *, pool_size: int = 5) -> None:
        cls.__pool = await create_pool(
            ConnectionData.DSN,
            min_size=pool_size,
            max_size=pool_size,
            max_inactive_connection_lifetime=120,
            command_timeout=60
        )

        logger.info('База данных подключена')

    @classmethod
    async def disconnect(cls) -> None:
        await cls.__pool.close()
        logger.info('База данных отключена')

    @classmethod
    async def __fetch(cls, compiled_query: str, depth: int = 0) -> list[Record]:
        if depth == 3:
            logger.error(f'Слишком много попыток получить данные из БД. Запрос: {compiled_query}')
            raise ConnectionDoesNotExistError()

        try:
            return await cls.__pool.fetch(compiled_query)
        except (CannotConnectNowError, ConnectionDoesNotExistError, ConnectionRefusedError):
            await sleep(3)
            return await cls.__fetch(compiled_query, depth + 1)

    @classmethod
    async def fetch(cls, query: Query, *, model: Model = None) -> list[Record | FunctionResult | T]:
        result = await cls.__fetch(cls.compile(query))

        if model is None:
            return result

        if isclass(model) and issubclass(model, BaseModel):
            return list(map(lambda record: model(**record), result))

        return list(map(model, result))

    @classmethod
    async def fetch_one(cls, query: Query, *, model: Model = None) -> Record | FunctionResult | T | None:
        return response[0] if (response := await cls.fetch(query, model=model)) else None

    @classmethod
    async def __execute(cls, compiled_query: str, depth: int = 0) -> None:
        if depth == 3:
            logger.error(f'Слишком много попыток добавить/изменить данные в БД. Запрос: {compiled_query}')
            raise ConnectionDoesNotExistError()

        try:
            await cls.__pool.execute(compiled_query)
        except (CannotConnectNowError, ConnectionDoesNotExistError, ConnectionRefusedError):
            await sleep(3)
            return await cls.__execute(compiled_query, depth + 1)

    @classmethod
    async def execute(cls, query: Query) -> None:
        await cls.__execute(cls.compile(query))

    @classmethod
    def compile(cls, query: Query) -> str:
        try:
            return query.compile(dialect=dialect(), compile_kwargs={"literal_binds": True}).string
        except CompileError as error:
            logger.exception()
            logger.error('Database: При компиляции запроса произошла ошибка')

            raise CompilationError(str(query)) from error

    @classmethod
    def compile_table(cls, table: type[Base]) -> str:
        return CreateTable(Base.metadata.tables[table.__tablename__]).compile(dialect=dialect()).string
