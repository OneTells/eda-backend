from typing import Literal, Self

from pydantic import BaseModel, Field


class Nutrient(BaseModel):
    value: float
    unit: Literal['г', 'ккал']

    def __hash__(self):
        return hash((type(self), self.value, self.unit))

    def __eq__(self, other: Self):
        return (self.value, self.unit) == (other.value, other.unit)


class Nutrients(BaseModel):
    calories: Nutrient
    proteins: Nutrient
    fats: Nutrient
    carbohydrates: Nutrient

    def __hash__(self):
        return hash((type(self), self.calories, self.proteins, self.fats, self.carbohydrates))

    def __eq__(self, other: Self):
        if other is None:
            return False

        return (self.calories, self.proteins, self.fats, self.carbohydrates) == (other.calories, other.proteins, other.fats, other.carbohydrates)


class Measure(BaseModel):
    value: float
    unit: Literal['g', 'kg', 'ml', 'l'] = Field(alias='measure_unit')

    def __hash__(self):
        return hash((type(self), self.value, self.unit))

    def __eq__(self, other: Self):
        if other is None:
            return False

        return (self.value, self.unit) == (other.value, other.unit)
