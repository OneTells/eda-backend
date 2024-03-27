from sqlalchemy import Text, SmallInteger, ForeignKey
from sqlalchemy.orm import mapped_column as column, Mapped

from core.general.models.base import Base


class Organizations(Base):
    __tablename__ = 'organizations'

    id: Mapped[int] = column(SmallInteger, autoincrement=True, primary_key=True)
    name: Mapped[str] = column(Text, unique=True)
    slug: Mapped[str] = column(Text, unique=True)
    photo: Mapped[str] = column(Text, unique=True)


class Restaurants(Base):
    __tablename__ = 'restaurants'

    id: Mapped[int] = column(SmallInteger, autoincrement=True, primary_key=True)
    slug: Mapped[str] = column(Text, unique=True)
    organization_id: Mapped[int] = column(SmallInteger, ForeignKey(Organizations.id), nullable=False)
