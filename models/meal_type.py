from enum import Enum


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

    @classmethod
    def values(cls):
        return [t.value for t in cls]

    @classmethod
    def from_str(cls, s: str) -> "MealType":
        try:
            return cls(s.lower())
        except ValueError:
            raise ValueError(f"Invalid meal type '{s}'. Must be one of: {cls.values()}")


# Meal slots used by the recommendation agent (excludes snack)
MEAL_SLOTS = [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER]
