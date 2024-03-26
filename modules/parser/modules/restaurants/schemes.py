from typing import Self

from pydantic import BaseModel


class Photo(BaseModel):
    uri: str


class Media(BaseModel):
    photos: list[Photo]


class Brand(BaseModel):
    slug: str


class Restaurant(BaseModel):
    name: str
    slug: str
    media: Media
    brand: Brand

    def __hash__(self):
        return hash((self.name, self.slug))

    def __eq__(self, other: Self):
        if type(self) != type(other):
            return False

        return (self.name, self.slug) == (other.name, other.slug)


class Location(BaseModel):
    latitude: float
    longitude: float
