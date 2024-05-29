from dataclasses import dataclass
from itertools import product
from re import sub
from typing import Iterable

from Levenshtein import ratio


@dataclass(frozen=True, slots=True)
class Allergen:
    id: int
    name: str


@dataclass(frozen=True, slots=True)
class SimilarWord:
    word: str
    allergen_id: str
    percent: int


class Searcher:
    __MATCH_PERCENTAGE = 65

    def __init__(self, allergens: list[Allergen]):
        self.__allergens = allergens

    @staticmethod
    def __word_comparison(first_word: str, second_word: str) -> int:
        return int(round(100 * ratio(first_word, second_word)))

    @staticmethod
    def __get_words(description: str) -> Iterable[str]:
        return (word for word in set(sub(r'[^0-9а-яa-z ]+', "", sub(r'-+', " ", description.lower())).split(' ')) if word)

    async def __call__(self, description: str) -> set[SimilarWord]:
        result = set()

        description_words = self.__get_words(description)

        for search_word, allergen in product(description_words, self.__allergens):
            word_comparison_percentage = self.__word_comparison(search_word, allergen.name)

            if word_comparison_percentage >= self.__MATCH_PERCENTAGE:
                result.add(SimilarWord(search_word, allergen.id, word_comparison_percentage))

        return result
