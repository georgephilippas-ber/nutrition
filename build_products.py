# https://fdc.nal.usda.gov/download-datasets.html

import json
import uuid
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any

from analysis import Score

# energy - unitName: ["kcal", "kJ"]
keys_original_array = ["Carbohydrate, by difference", "Total lipid (fat)", "Protein", "Fiber, total dietary",
                       "Sodium, Na",
                       "Sugars, Total", "Energy"]

keys_fundamental_nutrients_array = [
    "carbohydrates", "fat", "protein", "fiber", "sodium", "sugar", "energy"
]


@dataclass
class NutriscoreEvaluation:
    category: str
    score: float


@dataclass
class FoundationEvaluation:
    score: float


@dataclass
class ServingDescription:
    amount: int
    units: str


@dataclass
class EvaluationType:
    nutriscore: Optional[NutriscoreEvaluation]
    foundation: Optional[FoundationEvaluation]


@dataclass
class FundamentalNutrientsType:
    energy: float
    carbohydrates: float
    protein: float
    fat: float
    fiber: float
    sodium: float
    sugar: float


@dataclass
class ProductDesignationType:
    food: str
    name: str
    company: str
    characteristics: List[str]


@dataclass
class ProductType:
    id: str
    fundamental_nutrients: FundamentalNutrientsType
    product_designation: ProductDesignationType
    serving_size: float
    evaluation: EvaluationType
    serving_description: ServingDescription
    units: str


class FoodData:
    __FoundationFoods: List
    __score: Score

    def __init__(self):
        try:
            with open(
                    "./FoodData/foundationDownload.json") as foundationDownload:
                self.__FoundationFoods = json.load(foundationDownload)["FoundationFoods"]

            self.__score = Score(self.__FoundationFoods)
        except (FileNotFoundError, KeyError) as e:
            print(e)
            self.__FoundationFoods = []

    @staticmethod
    def __nutrient_by_name(food_object: Dict, nutrient_name: str, unit_name: str | None = None) -> Optional[Dict]:
        list_ = list(
            filter(lambda x: nutrient_name.lower() in x["nutrient"]["name"].lower() and (
                x["nutrient"]["unitName"] == unit_name if unit_name is not None else True),
                   food_object["foodNutrients"]))
        try:
            return list_[0]
        except IndexError:
            return None

    def length(self):
        return len(self.__FoundationFoods)

    def to_product(self, food_: Optional[Dict]) -> Any:
        if food_ is not None:
            nutrients_ = [
                *[self.__nutrient_by_name(food_, name_) for name_ in keys_original_array if name_ != "Energy"],
                self.__nutrient_by_name(food_, "Energy", "kcal")]

            serving_size = 3.e1

            serving_description: Optional[ServingDescription] = None

            try:
                serving_size = food_["foodPortions"][0]["gramWeight"]
                serving_description = ServingDescription(amount=food_["foodPortions"][0]["amount"],
                                                         units=food_["foodPortions"][0]["measureUnit"]["name"])
            except (IndexError, KeyError):
                pass

            fundamental_nutrients_dict = dict()

            food, *characteristics = food_["description"].split(", ")

            for (key_original, key_fundamental_nutrients, value) in zip(keys_original_array,
                                                                        keys_fundamental_nutrients_array, nutrients_):
                if key_fundamental_nutrients != "sodium":
                    fundamental_nutrients_dict[key_fundamental_nutrients] = value.get("amount",
                                                                                      0.) if value is not None else 0.
                else:
                    amount_ = value.get("amount") if value is not None else None
                    if amount_ is not None:
                        amount_ /= 1.e3
                    else:
                        amount_ = 0.

                    fundamental_nutrients_dict[key_fundamental_nutrients] = amount_

            fundamental_nutrients = FundamentalNutrientsType(**fundamental_nutrients_dict)

            product_designation = ProductDesignationType(food=food.lower(), characteristics=list(
                map(lambda x: x.lower(), characteristics)), name=food.lower(),
                                                         company="FoodData Central")

            foundation = FoundationEvaluation(score=self.__score.score_squeezed(food_))
            evaluation = EvaluationType(foundation=foundation, nutriscore=None)

            product = ProductType(id=", ".join(["foundation", uuid.uuid4().hex]),
                                  fundamental_nutrients=fundamental_nutrients,
                                  evaluation=evaluation, product_designation=product_designation,
                                  serving_size=serving_size,
                                  units="g", serving_description=serving_description)
            return product
        else:
            return None

    def find_by_name(self, name_: str) -> Optional[Dict]:
        try:
            return list(filter(lambda x: name_ in x["description"].lower(), self.__FoundationFoods))[0]
        except (IndexError, KeyError):
            return None

    def foundation_foods(self) -> List[Dict]:
        return self.__FoundationFoods


def write():
    food_data = FoodData()

    array_ = [asdict(food_data.to_product(foundation_food)) for foundation_food in food_data.foundation_foods()]

    with open("./food_data.json", "w") as food_data_file:
        json.dump(array_, food_data_file, indent=4)


if __name__ == "__main__":
    pass
