from typing import Literal

from pydantic import BaseModel


class Nutrient(BaseModel):
    value: float
    unit: Literal['г', 'ккал']


class Nutrients(BaseModel):
    calories: Nutrient
    proteins: Nutrient
    fats: Nutrient
    carbohydrates: Nutrient


class Measure(BaseModel):
    value: float
    measure_unit: Literal['g', 'kg', 'ml', 'l']
