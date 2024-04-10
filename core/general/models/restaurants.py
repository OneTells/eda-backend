from datetime import datetime

from sqlalchemy import Text, SmallInteger, ForeignKey, TIMESTAMP, Double, BigInteger
from sqlalchemy.orm import mapped_column as column, Mapped

from core.general.models.base import Base


class Organizations(Base):
    __tablename__ = 'organizations'

    id: Mapped[int] = column(BigInteger, autoincrement=True, primary_key=True)
    name: Mapped[str] = column(Text, unique=True)
    slug: Mapped[str] = column(Text, unique=True)
    photo: Mapped[str] = column(Text, nullable=False)


class Restaurants(Base):
    __tablename__ = 'restaurants'

    id: Mapped[int] = column(SmallInteger, autoincrement=True, primary_key=True)
    slug: Mapped[str] = column(Text, unique=True)
    organization_id: Mapped[int] = column(BigInteger, ForeignKey(Organizations.id), nullable=False)
    longitude: Mapped[float] = column(Double, nullable=False)
    latitude: Mapped[float] = column(Double, nullable=False)
    rating: Mapped[float] = column(Double)
    last_parsing_time: Mapped[datetime] = column(TIMESTAMP, nullable=False)
