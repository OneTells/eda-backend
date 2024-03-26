from typing import Literal

from pydantic import BaseModel

type Method = Literal['GET', 'POST', 'PUT', 'HEAD', 'DELETE']


class Response(BaseModel):
    content: bytes | None
    status_code: int
