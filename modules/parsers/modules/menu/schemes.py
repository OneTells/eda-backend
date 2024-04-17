from typing import Self

from pydantic import BaseModel

from core.general.schemes.menu import Measure, Nutrients


class Photo(BaseModel):
    uri: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    nutrients: Nutrients | None = None
    measure: Measure | None = None
    picture: Photo | None = None

    def __hash__(self):
        return hash((type(self), self.name))

    def __eq__(self, other: Self):
        return self.name == other.name


class Category(BaseModel):
    name: str
    items: list[Item]

    def __hash__(self):
        return hash((type(self), self.name, tuple(self.items)))

    def __eq__(self, other: Self):
        return (self.name, self.items) == (other.name, other.items)


class MenuItem(BaseModel):
    category_name: str

    name: str
    description: str | None
    price: float
    nutrients: Nutrients | None
    measure: Measure | None
    photo: str | None

    def __hash__(self):
        return hash((type(self), self.name, self.photo))

    def __eq__(self, other: Self):
        return (self.name, self.photo) == (other.name, self.photo)
