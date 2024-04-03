from sqlalchemy import Text, SmallInteger, Float, ForeignKey, BigInteger
from sqlalchemy.orm import mapped_column as column, Mapped

from core.general.models.base import Base
from core.general.models.restaurants import Restaurants


class MenuItems(Base):
    __tablename__ = 'menu_items'

    id: Mapped[int] = column(BigInteger, autoincrement=True, primary_key=True)
    name: Mapped[str] = column(Text, nullable=False)
    description: Mapped[str] = column(Text)
    price: Mapped[float] = column(Float, nullable=False)
    nutrient: Mapped[str | None] = column(Text)
    weight_in_grams: Mapped[float] = column(Float)
    photo: Mapped[str | None] = column(Text)
    restaurant_id: Mapped[int] = column(SmallInteger, ForeignKey(Restaurants.id), nullable=False)
