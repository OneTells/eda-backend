from pydantic import BaseModel


class Restaurant(BaseModel):
    id: int
    name: str
    rating: float | None
    distance: float
    photo: str
