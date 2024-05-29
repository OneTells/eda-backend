from sqlalchemy import Text, SmallInteger, BigInteger, ForeignKey
from sqlalchemy.orm import mapped_column as column, Mapped

from core.general.models.base import Base


class Allergens(Base):
    __tablename__ = 'allergens'

    id: Mapped[int] = column(SmallInteger, autoincrement=True, primary_key=True)
    title: Mapped[str] = column(Text, nullable=False)


class AllergenMatches(Base):
    __tablename__ = 'allergen_matches'

    id: Mapped[int] = column(BigInteger, autoincrement=True, primary_key=True)
    allergen_id: Mapped[int] = column(SmallInteger, ForeignKey(Allergens.id), nullable=False)
    word: Mapped[str] = column(Text, nullable=False)
    percent: Mapped[int] = column(SmallInteger, nullable=False)
