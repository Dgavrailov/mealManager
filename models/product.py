from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    name: str
    quantity: str = ""
    meal_id: Optional[int] = None
    id: Optional[int] = None

    def display(self) -> str:
        return f"{self.name} ({self.quantity})" if self.quantity else self.name

    def to_dict(self) -> dict:
        return {"id": self.id, "meal_id": self.meal_id, "name": self.name, "quantity": self.quantity}
