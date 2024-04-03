from core.general.models.allergens import Allergens
from core.modules.database.methods import Select
from modules.api.modules.allergens.schemes import Allergen


class AllergenDB:

    @staticmethod
    async def get_all() -> list[Allergen]:
        return await Select(Allergens.id, Allergens.title).fetch(model=Allergen)
