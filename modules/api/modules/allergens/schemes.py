from pydantic import BaseModel


class Allergen(BaseModel):
    id: int
    title: str
    is_selected: bool
