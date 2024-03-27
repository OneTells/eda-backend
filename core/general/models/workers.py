from sqlalchemy import Text, Boolean, false
from sqlalchemy.orm import mapped_column as column, Mapped

from core.general.models.base import Base


class Workers(Base):
    __tablename__ = 'workers'

    name: Mapped[str] = column(Text, unique=True, primary_key=True)
    is_trigger_on: Mapped[bool] = column(Boolean, nullable=False, server_default=false())
