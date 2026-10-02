from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

from .meal_type import MealType
from .product import Product


@dataclass
class Meal:
    name: str
    meal_type: MealType
    meal_date: date
    products: List[Product] = field(default_factory=list)
    notes: str = ""
    recipe: str = ""
    calories: Optional[int] = None
    id: Optional[int] = None

    def product_names(self) -> List[str]:
        return [p.name for p in self.products]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "meal_type": self.meal_type.value,
            "meal_date": self.meal_date.isoformat(),
            "notes": self.notes,
            "recipe": self.recipe,
            "calories": self.calories,
            "products": [p.to_dict() for p in self.products],
        }

    def to_summary_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "meal_type": self.meal_type.value,
            "meal_date": self.meal_date.isoformat(),
            "product_count": len(self.products),
            "has_recipe": bool(self.recipe),
            "calories": self.calories,
        }
