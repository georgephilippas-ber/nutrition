from typing import List, Dict, Tuple, Optional, Callable
import json


def nutrients() -> List[Tuple[str, str]]:
    nutrients_: List[Tuple[str, str]] = []

    for foundation_food in data_foundation():
        for food_nutrient in foundation_food["foodNutrients"]:
            if food_nutrient["nutrient"]["name"] not in list(map(lambda x: x[0], nutrients_)) and \
                    food_nutrient["nutrient"].get("unitName") is not None:
                nutrients_.append((food_nutrient["nutrient"]["name"], food_nutrient["nutrient"].get("unitName")))

    return nutrients_


def data_legacy() -> List[Dict]:
    with open("./FoodData/FoodData_Central_sr_legacy_food_json_2021-10-28.json") as foundationDownload:
        return json.load(foundationDownload)["SRLegacyFoods"]


def data_foundation() -> List[Dict]:
    with open("./FoodData/foundationDownload.json") as foundationDownload:
        return json.load(foundationDownload)["FoundationFoods"]


def to_idx(list_: List[Tuple], index: int) -> List:
    return list(map(lambda x: x[index], list_))


def to_idx_filtered(list_: List[Tuple], index: int, condition: Callable[[], bool]) -> List:
    return list(filter(condition, to_idx(list_, index)))
