from fastapi import APIRouter

from modules.api.modules.allergens.database import AllergenDB

router = APIRouter(prefix='/allergens')


@router.get("/all")
async def get_all():
    return await AllergenDB.get_all()
