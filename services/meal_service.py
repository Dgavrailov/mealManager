"""Business logic for meal management."""

from datetime import date
from typing import Dict, List, Optional

from models.meal import Meal
from models.product import Product
from repo.meal_repo import MealRepo


class MealService:
    def __init__(self, meal_repo: MealRepo):
        self.repo = meal_repo

    def add_meal(self, data: Dict, user_id: Optional[int] = None) -> Meal:
        products = [Product(name=p["name"], quantity=p["quantity"]) for p in data.get("products", [])]
        meal = Meal(
            name=data["name"],
            meal_type=data["meal_type"],
            meal_date=data["meal_date"],
            products=products,
            notes=data.get("notes", ""),
            recipe=data.get("recipe", ""),
            calories=data.get("calories"),
        )
        return self.repo.create(meal, user_id=user_id)

    def update_meal(self, meal_id: int, data: Dict, user_id: Optional[int] = None) -> Optional[Meal]:
        if self.repo.get_by_id(meal_id, user_id=user_id) is None:
            return None
        products = [Product(name=p["name"], quantity=p["quantity"]) for p in data.get("products", [])]
        meal = Meal(
            id=meal_id,
            name=data["name"],
            meal_type=data["meal_type"],
            meal_date=data["meal_date"],
            products=products,
            notes=data.get("notes", ""),
            recipe=data.get("recipe", ""),
            calories=data.get("calories"),
        )
        return self.repo.update(meal, user_id=user_id)

    def delete_meal(self, meal_id: int, user_id: Optional[int] = None) -> bool:
        return self.repo.delete(meal_id, user_id=user_id)

    def get_meal(self, meal_id: int, user_id: Optional[int] = None) -> Optional[Meal]:
        return self.repo.get_by_id(meal_id, user_id=user_id)

    def get_by_date(self, meal_date: date, user_id: Optional[int] = None) -> List[Meal]:
        return self.repo.get_by_date(meal_date, user_id=user_id)

    def get_all(self, user_id: Optional[int] = None) -> List[Meal]:
        return self.repo.get_all(user_id=user_id)

    def get_range(self, start: date, end: date, user_id: Optional[int] = None) -> List[Meal]:
        return self.repo.get_range(start, end, user_id=user_id)
