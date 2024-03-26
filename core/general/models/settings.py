from sqlalchemy import Text
from sqlalchemy.orm import mapped_column as column, Mapped

from core.general.models.base import Base


class Settings(Base):
    __tablename__ = 'settings'

    name: Mapped[str] = column(Text, unique=True, primary_key=True)
    value: Mapped[str] = column(Text, nullable=False)
