from typing import Literal, Mapping, Any

from aiohttp import ClientResponse
from pydantic import BaseModel, ConfigDict, Field

type Methods = Literal['GET', 'POST', 'PUT', 'DELETE']

type Dict = Mapping[str, str]
type Params = Mapping[str, str | int | float]


class Response(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    content: bytes | None
    status_code: int

    row_response: ClientResponse | None


class RequestArgs(BaseModel):
    model_config = ConfigDict(extra='forbid')

    params: Params | None = None
    data: Any = None
    json_: Any = Field(None, alias='json')
    cookies: Dict | None = None
    headers: Dict | None = None
