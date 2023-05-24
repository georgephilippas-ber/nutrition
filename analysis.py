from __future__ import annotations

from enum import Enum
from typing import Dict, Optional, List, Tuple

nutrients = {
    "harmful": [
        ("Total lipid (fat)", "g", 81, 0.1),  # Worst food: Fast food french fries
        ("Sodium, Na", "mg", 1500, 0.2),  # Worst food: Processed meats (e.g., deli ham)
        ("Fatty acids, total saturated", "g", 20, 0.25),  # Worst food: Butter
        ("Cholesterol", "mg", 573, 0.25),  # Worst food: Egg yolk
        ("Sugars, Total", "g", 10.6, 0.2)  # Worst food: Coca-Cola
    ],
    "beneficial": [
        ("Protein", "g", 31, 0.15),  # Chicken breast
        ("Fiber, total dietary", "g", 25, 0.15),  # Chia seeds
        ("Calcium, Ca", "mg", 1300, 0.15),  # Low-fat milk
        ("Magnesium, Mg", "mg", 262., 0.1),  # Pumpkin seeds
        ("Vitamin C, total ascorbic acid", "mg", 90, 0.10),  # Kiwi fruit
        ("Iron, Fe", "mg", 17.9, 0.1),  # Beef liver
        ("Phosphorus, P", "mg", 700, 0.05),  # Parmesan cheese
        ("Copper, Cu", "mg", 0.5, 0.025),  # Cashews
        ("Manganese, Mn", "mg", 1.0, 0.025),  # Pine nuts
        ("Potassium, K", "mg", 4700, 0.05),  # Avocado
        ("Zinc, Zn", "mg", 30, 0.05),  # Oysters
        ("Vitamin A, RAE", "µg", 700, 0.05)  # Carrots
    ]
}


def nutrient(name: str, food: Dict) -> Optional[Dict]:
    list_ = list(filter(lambda x: x["nutrient"]["name"] == name, food["foodNutrients"]))

    if list_:
        try:
            return {
                "amount": list_[0]["amount"],
                "name": list_[0]["nutrient"]["name"],
                "unitName": list_[0]["nutrient"]["unitName"]
            }
        except KeyError:
            return None
    else:
        return None


class Collection(Enum):
    BENEFICIAL = 0
    HARMFUL = 1

    @staticmethod
    def get(collection: Collection):
        match collection:
            case Collection.BENEFICIAL:
                return "beneficial"
            case Collection.HARMFUL:
                return "harmful"


class Score:
    __data: List[Dict]

    def __init__(self, data: List[Dict]):
        self.__data = data

    @staticmethod
    def score_aspect(food: Dict, collection: Collection) -> float:
        cumulative = 0.
        weight_cumulative = 0.

        for nutrient_tuple in nutrients[Collection.get(collection)]:
            value_ = nutrient(nutrient_tuple[0], food)

            if value_:
                cumulative += min(value_["amount"] / nutrient_tuple[2] * nutrient_tuple[3], 1.)
                weight_cumulative += nutrient_tuple[3]

        return cumulative / (weight_cumulative if weight_cumulative > 0 else 1)

    @staticmethod
    def score(food: Dict):
        return Score.score_aspect(food, Collection.BENEFICIAL) - Score.score_aspect(food, Collection.HARMFUL)

    @staticmethod
    def statistics(data: List[Dict]) -> Tuple[float, float, float]:
        array_ = [Score.score(entry_) for entry_ in data]

        return min(array_), max(array_), max(array_) - min(array_)

    def score_normalized(self, food: Dict) -> float:
        min_, max_, range_ = Score.statistics(self.__data)

        return (Score.score(food) - min_) / range_

    def score_squeezed(self, food: Dict, factor: float = 0.5, min_: float = 0.5):
        return self.score_normalized(food) * factor + min_


def check_weights():
    return int(sum(map(lambda x: x[3], nutrients[Collection.get(Collection.BENEFICIAL)]))) == int(
        sum(map(lambda x: x[3], nutrients[Collection.get(Collection.HARMFUL)]))) == 1
