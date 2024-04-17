from dataclasses import dataclass
from typing import Self

from pydantic import BaseModel


@dataclass(frozen=True, slots=True)
class RestaurantAdditionalData:
    longitude: float
    latitude: float
    rating: float | None


class Organization(BaseModel):
    slug: str

    name: str
    photo: str


class Restaurant(BaseModel):
    slug: str

    organization: Organization
    longitude: float
    latitude: float
    rating: float | None

    def __hash__(self):
        return hash((type(self), self.slug))

    def __eq__(self, other: Self):
        return (self.slug, ) == (other.slug, )
