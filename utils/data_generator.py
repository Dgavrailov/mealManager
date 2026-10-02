"""Seeds the database with 14 days of realistic sample meals."""

import random
from datetime import date, timedelta

from models.meal import Meal
from models.meal_type import MealType
from models.product import Product
from repo.meal_repo import MealRepo

_SAMPLES = {
    MealType.BREAKFAST: [
        ("Oatmeal with berries",   [("oats","100g"),("milk","200ml"),("blueberries","50g"),("honey","1 tsp")]),
        ("Scrambled eggs & toast", [("eggs","3 pcs"),("bread","2 slices"),("butter","10g")]),
        ("Greek yogurt parfait",   [("greek yogurt","150g"),("granola","40g"),("strawberries","80g")]),
        ("Avocado toast",          [("bread","2 slices"),("avocado","1 pcs"),("lemon","½ pcs")]),
        ("Banana pancakes",        [("banana","1 pcs"),("egg","2 pcs"),("flour","80g"),("maple syrup","2 tbsp")]),
        ("Smoothie bowl",          [("frozen mango","100g"),("banana","1 pcs"),("spinach","30g")]),
        ("Cottage cheese & fruit", [("cottage cheese","150g"),("peach","1 pcs"),("honey","1 tsp")]),
    ],
    MealType.LUNCH: [
        ("Grilled chicken salad",  [("chicken breast","150g"),("lettuce","80g"),("tomato","1 pcs"),("olive oil","1 tbsp")]),
        ("Lentil soup",            [("lentils","120g"),("carrot","1 pcs"),("onion","1 pcs"),("cumin","1 tsp")]),
        ("Tuna wrap",              [("tuna","100g"),("tortilla","1 pcs"),("cucumber","½ pcs"),("mayo","1 tbsp")]),
        ("Vegetable stir-fry",     [("rice","150g"),("broccoli","100g"),("bell pepper","1 pcs"),("soy sauce","2 tbsp")]),
        ("Caprese sandwich",       [("ciabatta","1 pcs"),("mozzarella","80g"),("tomato","2 pcs"),("basil","5g")]),
        ("Quinoa & roasted veggies",[("quinoa","120g"),("zucchini","1 pcs"),("red onion","1 pcs"),("feta","40g")]),
        ("Minestrone soup",        [("pasta","80g"),("kidney beans","100g"),("tomato","2 pcs"),("celery","1 stalk")]),
    ],
    MealType.DINNER: [
        ("Baked salmon & asparagus",[("salmon","180g"),("asparagus","100g"),("lemon","1 pcs"),("garlic","2 cloves")]),
        ("Beef stir-fry & noodles", [("beef strips","150g"),("noodles","120g"),("bok choy","80g"),("oyster sauce","2 tbsp")]),
        ("Chicken tikka masala",    [("chicken","200g"),("tomato sauce","150ml"),("cream","50ml"),("garam masala","2 tsp")]),
        ("Pasta primavera",         [("pasta","150g"),("cherry tomatoes","100g"),("zucchini","1 pcs"),("parmesan","30g")]),
        ("Black bean tacos",        [("tortilla","2 pcs"),("black beans","120g"),("salsa","50g"),("avocado","1 pcs")]),
        ("Mushroom risotto",        [("arborio rice","150g"),("mushrooms","120g"),("white wine","50ml"),("parmesan","30g")]),
        ("Grilled pork & salad",    [("pork chops","180g"),("lettuce","60g"),("apple","1 pcs"),("mustard","1 tsp")]),
    ],
}


class DataGenerator:
    def __init__(self, meal_repo: MealRepo):
        self.repo = meal_repo

    def seed(self, days: int = 14) -> int:
        today = date.today()
        inserted = 0
        for offset in range(days, 0, -1):
            day = today - timedelta(days=offset)
            existing_types = {m.meal_type for m in self.repo.get_by_date(day)}
            for meal_type in MealType:
                if meal_type in existing_types:
                    continue
                name, raw = random.choice(_SAMPLES[meal_type])
                products = [Product(name=n, quantity=q) for n, q in raw]
                self.repo.create(Meal(name=name, meal_type=meal_type, meal_date=day, products=products))
                inserted += 1
        return inserted
