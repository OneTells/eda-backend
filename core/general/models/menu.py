from datetime import datetime

from sqlalchemy import Text, Float, ForeignKey, BigInteger, TIMESTAMP, SmallInteger
from sqlalchemy.orm import mapped_column as column, Mapped

from core.general.models.allergen import AllergenMatches
from core.general.models.base import Base
from core.general.models.restaurants import Restaurants


class Categories(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = column(BigInteger, autoincrement=True, primary_key=True)
    name: Mapped[str] = column(Text, nullable=False)


class MenuItems(Base):
    __tablename__ = 'menu_items'

    id: Mapped[int] = column(BigInteger, autoincrement=True, primary_key=True)
    name: Mapped[str] = column(Text, nullable=False)
    description: Mapped[str | None] = column(Text)
    price: Mapped[float] = column(Float, nullable=False)
    nutrients: Mapped[str | None] = column(Text)
    measure: Mapped[str | None] = column(Text)
    photo: Mapped[str | None] = column(Text)
    restaurant_id: Mapped[int] = column(BigInteger, ForeignKey(Restaurants.id), nullable=False)
    last_parsing_time: Mapped[datetime] = column(TIMESTAMP, nullable=False)
    category_id: Mapped[int] = column(BigInteger, ForeignKey(Categories.id), nullable=False)

    description_hash: Mapped[str] = column(Text)


class MenuItemAllergens(Base):
    __tablename__ = 'menu_item_allergens'

    allergen_match_id: Mapped[int] = column(SmallInteger, ForeignKey(AllergenMatches.id), primary_key=True)
    menu_item_id: Mapped[int] = column(BigInteger, ForeignKey(MenuItems.id), primary_key=True)
