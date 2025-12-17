from enum import Enum
from random import randint


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NONE = "none"

class GenderRate(Enum):
    GENDERLESS = -1
    ALWAYS_FEMALE = 0
    MOSTLY_FEMALE = 1
    MAJORITY_FEMALE = 2
    LIKELY_FEMALE = 3
    EQUAL = 4
    LIKELY_MALE = 5
    MAJORITY_MALE = 6
    MOSTLY_MALE = 7
    ALWAYS_MALE = 8


def calculate_gender(rate: GenderRate) -> Gender:
    if rate == -1:
        return Gender.NONE
    roll = randint(1, 100)
    if roll <= (8 - rate.value) * 12.5:
        return Gender.MALE
    else:
        return Gender.FEMALE