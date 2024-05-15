from pydantic import BaseModel


class Content[T: BaseModel](BaseModel):
    content: T | None
