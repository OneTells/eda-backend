from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func

from core.general.models.allergen import Allergens
from core.general.models.user import UserAllergen
from core.modules.database.methods.requests import Select, Update, Insert
from modules.api.core.methods.auth import get_user_id
from modules.api.modules.allergens.schemes import Allergen

router = APIRouter(prefix='/allergens', tags=['allergens'])


@router.get("/")
async def get_all(user_id: Annotated[int, Depends(get_user_id)]):
    data = await (
        Select(Allergens.id.distinct(), Allergens.title, UserAllergen.is_selected)
        .outerjoin(UserAllergen, Allergens.id == UserAllergen.allergen_id)
        .where(UserAllergen.user_id.is_(None) | (UserAllergen.user_id == user_id))
        .order_by(Allergens.title)
        .fetch()
    )

    return list(map(lambda x: Allergen(id=x[0], title=x[1], is_selected=bool(x[2])), data))


@router.put("/")
async def select(user_id: Annotated[int, Depends(get_user_id)], allergen_id: str, is_selected: bool):
    is_exist = await (
        Select(func.count())
        .where(UserAllergen.user_id == user_id, UserAllergen.allergen_id == allergen_id)
        .fetch_one(model=lambda x: bool(x[0]))
    )

    if is_exist:
        await (
            Update(UserAllergen)
            .values(is_selected=is_selected)
            .where(UserAllergen.user_id == user_id, UserAllergen.allergen_id == allergen_id)
            .execute()
        )
        return

    await (
        Insert(UserAllergen)
        .values(user_id=user_id, allergen_id=allergen_id, is_selected=is_selected)
        .execute()
    )
