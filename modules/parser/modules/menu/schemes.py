from typing import Self

from pydantic import BaseModel


class Photo(BaseModel):
    uri: str


class Nutrient(BaseModel):
    name: str
    value: float
    unit: str


class Nutrients(BaseModel):
    calories: Nutrient
    proteins: Nutrient
    fats: Nutrient
    carbohydrates: Nutrient


class Measure(BaseModel):
    value: float
    measure_unit: str


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
