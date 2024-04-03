from sqlalchemy import Text, SmallInteger
from sqlalchemy.orm import mapped_column as column, Mapped

from core.general.models.base import Base


class Allergens(Base):
    __tablename__ = 'allergens'

    id: Mapped[int] = column(SmallInteger, autoincrement=True, primary_key=True)
    title: Mapped[str] = column(Text, nullable=False)
