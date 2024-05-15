from typing import Annotated

from fastapi import APIRouter, Depends

from core.general.models.restaurants import Restaurants, Organizations
from core.general.models.user import UserHistory
from core.modules.database.modules.requests.methods import Select
from modules.api.core.methods.auth import authorization
from modules.api.modules.history.schemes import Record

router = APIRouter(prefix='/history', tags=['history'])


@router.get("/")
async def get_all(user_id: Annotated[int, Depends(authorization)]):
    data = await (
        Select(Restaurants.id.distinct(), Organizations.name, Organizations.photo, UserHistory.created_at)
        .join(Organizations, Organizations.id == Restaurants.organization_id)
        .join(UserHistory, UserHistory.restaurant_id == Restaurants.id)
        .where(UserHistory.user_id == user_id)
        .order_by(UserHistory.created_at.desc())
        .fetch()
    )

    return list(map(lambda x: Record(id=x[0], title=x[1], photo=x[2], created_at=x[3]), data))
