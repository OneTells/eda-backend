from fastapi import APIRouter

from core.general.models.allergens import Allergens
from core.modules.database.modules.requests.methods import Select
from modules.api.modules.allergens.schemes import Allergen

router = APIRouter(prefix='/allergens')


@router.get("/all")
async def get_all():
    return await Select(Allergens.id, Allergens.title).fetch(model=Allergen)
