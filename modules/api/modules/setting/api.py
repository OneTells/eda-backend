from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func

from core.general.models.setting import Setting
from core.general.models.user import UserSetting
from core.modules.database.modules.requests.methods import Select, Update, Insert
from modules.api.core.methods.auth import authorization
from modules.api.modules.setting.schemes import SettingData

router = APIRouter(prefix='/setting', tags=['setting'])


@router.get("/")
async def get_all(user_id: Annotated[int, Depends(authorization)]):
    data = await (
        Select(Setting.id.distinct(), UserSetting.value)
        .outerjoin(UserSetting, Setting.id == UserSetting.setting_id)
        .where(UserSetting.user_id.is_(None) | (UserSetting.user_id == user_id))
        .order_by(Setting.id)
        .fetch()
    )

    return list(map(lambda x: SettingData(id=x[0], value=x[1] or 5), data))


@router.put("/")
async def select(user_id: Annotated[int, Depends(authorization)], setting_id: int, value: int):
    is_exist = await (
        Select(func.count())
        .where(UserSetting.user_id == user_id, UserSetting.setting_id == setting_id)
        .fetch_one(model=lambda x: bool(x[0]))
    )

    if is_exist:
        await (
            Update(UserSetting)
            .values(value=value)
            .where(UserSetting.user_id == user_id, UserSetting.setting_id == setting_id)
            .execute()
        )
        return

    await (
        Insert(UserSetting)
        .values(user_id=user_id, setting_id=setting_id, value=value)
        .execute()
    )
