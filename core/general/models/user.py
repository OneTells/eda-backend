from datetime import datetime

from sqlalchemy import Text, SmallInteger, Uuid, UUID, ForeignKey, Boolean, false, text, TIMESTAMP, BigInteger
from sqlalchemy.orm import mapped_column as column, Mapped

from core.general.models.allergen import Allergens
from core.general.models.base import Base
from core.general.models.restaurants import Restaurants
from core.general.models.setting import Setting


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = column(SmallInteger, autoincrement=True, primary_key=True)
    uuid: Mapped[UUID] = column(Uuid, nullable=True)
    login: Mapped[str] = column(Text, nullable=False)
    password_hash: Mapped[str] = column(Text, nullable=False)


class UserAllergen(Base):
    __tablename__ = 'user_allergens'

    user_id: Mapped[int] = column(SmallInteger, ForeignKey(User.id), primary_key=True)
    allergen_id: Mapped[int] = column(SmallInteger, ForeignKey(Allergens.id), primary_key=True)
    is_selected: Mapped[bool] = column(Boolean, nullable=False, server_default=false())


class UserSetting(Base):
    __tablename__ = 'user_settings'

    user_id: Mapped[int] = column(SmallInteger, ForeignKey(User.id), primary_key=True)
    setting_id: Mapped[int] = column(SmallInteger, ForeignKey(Setting.id), primary_key=True)
    value: Mapped[int] = column(SmallInteger, nullable=False, server_default=text("5"))


class UserHistory(Base):
    __tablename__ = 'user_history'

    id: Mapped[int] = column(BigInteger, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = column(SmallInteger, ForeignKey(User.id))
    restaurant_id: Mapped[int] = column(SmallInteger, ForeignKey(Restaurants.id))
    created_at: Mapped[datetime] = column(TIMESTAMP, nullable=False, server_default=text("now()"))
