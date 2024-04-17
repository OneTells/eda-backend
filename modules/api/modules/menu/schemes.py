from typing import Literal, Self

from pydantic import BaseModel

from core.general.schemes.menu import Nutrients


class Measure(BaseModel):
    value: float
    unit: Literal['g', 'kg', 'ml', 'l']

    def __hash__(self):
        return hash((type(self), self.value, self.unit))

    def __eq__(self, other: Self):
        if other is None:
            return False

        return (self.value, self.unit) == (other.value, other.unit)


class MenuItem(BaseModel):
    name: str
    description: str
    price: float
    nutrients: Nutrients | None
    measure: Measure | None
    photo: str | None


class Category(BaseModel):
    name: str
    menu_items: list[MenuItem]


class Menu(BaseModel):
    categories: list[Category]
