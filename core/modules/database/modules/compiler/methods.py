from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.exc import CompileError
from sqlalchemy.sql.ddl import CreateTable

from core.general.models.base import Base
from core.modules.database.core.schemes import Query
from core.modules.database.modules.compiler.exceptions import CompilationError


class Compiler:

    @classmethod
    def compile_query(cls, query: Query) -> str:
        try:
            return query.compile(dialect=dialect(), compile_kwargs={"literal_binds": True}).string
        except CompileError as error:
            raise CompilationError(query) from error

    @classmethod
    def compile_table(cls, table: type[Base]) -> str:
        return CreateTable(Base.metadata.tables[table.__tablename__]).compile(dialect=dialect()).string
