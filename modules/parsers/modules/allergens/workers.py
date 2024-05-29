import hashlib
from datetime import timedelta, datetime

from core.general.methods.workers import Lifespan
from core.general.models.allergen import Allergens, AllergenMatches
from core.general.models.menu import MenuItems, MenuItemAllergens
from core.general.utils.timer import timer
from core.modules.database.methods.requests import Select, Update, Insert
from core.modules.worker.abstract.executor import BaseExecutor
from core.modules.worker.abstract.trigger import BaseTrigger
from core.modules.worker.abstract.worker import BaseWorker
from core.modules.worker.schemes.setting import Setting
from modules.parsers.modules.allergens.methods import Searcher, Allergen, SimilarWord


class Executor(BaseExecutor, Lifespan):

    async def __call__(self, menu_item_id: int, description: str, searcher: Searcher, new_description_hash: str) -> None:
        result = await searcher(description)

        await self.add_new_data(result)
        await self.add_allergens_to_menu_item(menu_item_id, result)

        await (
            Update(MenuItems)
            .where(MenuItems.id == menu_item_id)
            .values(description_hash=new_description_hash)
            .execute()
        )

    @staticmethod
    async def add_allergens_to_menu_item(menu_item_id: int, result: set[SimilarWord]) -> None:
        allergens = await (
            Select(AllergenMatches.id, AllergenMatches.allergen_id, AllergenMatches.word)
            .fetch()
        )

        allergens_dict = {(word[1], word[2]): word[0] for word in allergens}

        allergen_match_ids = []

        for word in result:
            allergen_match_ids.append(allergens_dict.get((word.allergen_id, word.word)))

        if not allergen_match_ids:
            return

        await (
            Insert(MenuItemAllergens)
            .values([{'menu_item_id': menu_item_id, 'allergen_match_id': match_id} for match_id in allergen_match_ids])
            .on_conflict_do_nothing()
            .execute()
        )

    @staticmethod
    async def add_new_data(result: set[SimilarWord]) -> None:
        allergens: list[tuple] = await (
            Select(AllergenMatches.allergen_id, AllergenMatches.word)
            .fetch(model=tuple)
        )

        add_to_db = []

        for word in result:
            if (word.allergen_id, word.word) in allergens:
                continue

            add_to_db.append(dict(allergen_id=word.allergen_id, word=word.word, percent=word.percent))

        if not add_to_db:
            return

        await (
            Insert(AllergenMatches)
            .values(add_to_db)
            .execute()
        )


class Trigger(BaseTrigger, Lifespan):

    async def __call__(self) -> list[tuple]:
        allergens: list[Allergen] = sorted(
            await (
                Select(Allergens.id, Allergens.title)
                .fetch(model=lambda x: Allergen(id=x[0], name=x[1].lower()))
            ),
            key=lambda x: x.id
        )

        hash_allergens = hashlib.sha256(str(allergens).encode()).hexdigest()

        menu_items = await (
            Select(MenuItems.id, MenuItems.description, MenuItems.description_hash)
            .where(
                MenuItems.description.is_not(None),
                MenuItems.last_parsing_time + timedelta(days=3) > datetime.now()
            ).fetch()
        )

        result = []
        searcher = Searcher(allergens)

        for menu_item in menu_items:
            new_description_hash = hashlib.sha256(str([menu_item['description'], hash_allergens]).encode()).hexdigest()

            if menu_item['description_hash'] != new_description_hash:
                result.append((menu_item['id'], menu_item['description'], searcher, new_description_hash))

        return result


class AllergenParserWorker(BaseWorker):

    @staticmethod
    def setting() -> Setting:
        return Setting(timeout=timer(hours=24), executor_count=1)

    @staticmethod
    def executor() -> type[BaseExecutor]:
        return Executor

    @staticmethod
    def trigger() -> type[BaseTrigger]:
        return Trigger
