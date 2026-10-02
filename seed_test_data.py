"""
Seed 20 realistic meals per type for a given user_id, then test the recommender.
Run: python3.11 seed_test_data.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import date, timedelta
from repo.database import Database
from repo.meal_repo import MealRepo
from repo.template_repo import TemplateRepo
from services.recommendation_agent import RecommendationAgent

USER_ID = 2  # dgavrailov

BREAKFASTS = [
    ("Scrambled Eggs",        [("Eggs","3"),("Butter","1 tbsp"),("Salt","pinch")]),
    ("Oatmeal with Berries",  [("Oats","80g"),("Milk","200ml"),("Blueberries","50g"),("Honey","1 tsp")]),
    ("Avocado Toast",         [("Bread","2 slices"),("Avocado","1"),("Lemon juice","1 tsp"),("Salt","pinch")]),
    ("Greek Yogurt Bowl",     [("Greek yogurt","200g"),("Granola","40g"),("Banana","1"),("Honey","1 tsp")]),
    ("Pancakes",              [("Flour","150g"),("Egg","1"),("Milk","200ml"),("Butter","1 tbsp"),("Maple syrup","2 tbsp")]),
    ("Smoothie Bowl",         [("Frozen banana","1"),("Spinach","30g"),("Almond milk","150ml"),("Chia seeds","1 tbsp")]),
    ("Cheese Omelette",       [("Eggs","3"),("Cheddar","40g"),("Butter","1 tbsp"),("Chives","1 tbsp")]),
    ("Overnight Oats",        [("Oats","80g"),("Milk","200ml"),("Chia seeds","1 tbsp"),("Strawberries","60g")]),
    ("French Toast",          [("Bread","2 slices"),("Egg","2"),("Milk","50ml"),("Cinnamon","1/2 tsp"),("Maple syrup","1 tbsp")]),
    ("Banana Porridge",       [("Oats","80g"),("Banana","1"),("Milk","250ml"),("Peanut butter","1 tbsp")]),
    ("Egg Muffins",           [("Eggs","4"),("Bell pepper","1/2"),("Spinach","30g"),("Feta","30g")]),
    ("Chia Pudding",          [("Chia seeds","3 tbsp"),("Coconut milk","200ml"),("Mango","1/2"),("Honey","1 tsp")]),
    ("Bagel with Cream Cheese",[("Bagel","1"),("Cream cheese","2 tbsp"),("Smoked salmon","50g"),("Capers","1 tsp")]),
    ("Muesli",                [("Muesli mix","80g"),("Milk","200ml"),("Apple","1/2"),("Raisins","20g")]),
    ("Breakfast Burrito",     [("Tortilla","1"),("Eggs","2"),("Black beans","50g"),("Salsa","2 tbsp"),("Cheddar","30g")]),
    ("Waffles",               [("Waffle mix","150g"),("Egg","1"),("Milk","180ml"),("Butter","1 tbsp"),("Berries","50g")]),
    ("Poached Eggs on Toast",  [("Eggs","2"),("Bread","2 slices"),("Spinach","30g"),("Hollandaise","1 tbsp")]),
    ("Cottage Cheese Bowl",   [("Cottage cheese","200g"),("Pineapple","60g"),("Walnuts","20g"),("Honey","1 tsp")]),
    ("Peanut Butter Toast",   [("Bread","2 slices"),("Peanut butter","2 tbsp"),("Banana","1"),("Honey","1 tsp")]),
    ("Shakshuka",             [("Eggs","3"),("Tomatoes","2"),("Bell pepper","1"),("Onion","1"),("Cumin","1 tsp")]),
]

LUNCHES = [
    ("Caesar Salad",          [("Romaine lettuce","100g"),("Chicken breast","120g"),("Parmesan","20g"),("Caesar dressing","2 tbsp"),("Croutons","30g")]),
    ("Chicken Wrap",          [("Tortilla","1"),("Chicken breast","120g"),("Lettuce","30g"),("Tomato","1"),("Hummus","2 tbsp")]),
    ("Tomato Soup",           [("Tomatoes","400g"),("Onion","1"),("Garlic","2 cloves"),("Cream","50ml"),("Basil","5g")]),
    ("Tuna Sandwich",         [("Bread","2 slices"),("Tuna","1 can"),("Mayo","1 tbsp"),("Celery","1 stalk"),("Lettuce","20g")]),
    ("Quinoa Bowl",           [("Quinoa","100g"),("Chickpeas","80g"),("Cucumber","1/2"),("Feta","30g"),("Olive oil","1 tbsp")]),
    ("Grilled Chicken Salad", [("Chicken breast","150g"),("Mixed greens","80g"),("Cherry tomatoes","60g"),("Balsamic","1 tbsp")]),
    ("Lentil Soup",           [("Red lentils","150g"),("Carrot","1"),("Onion","1"),("Cumin","1 tsp"),("Vegetable stock","500ml")]),
    ("BLT Sandwich",          [("Bread","2 slices"),("Bacon","3 strips"),("Lettuce","20g"),("Tomato","1"),("Mayo","1 tbsp")]),
    ("Pasta Salad",           [("Pasta","100g"),("Cherry tomatoes","60g"),("Olives","30g"),("Feta","40g"),("Pesto","1 tbsp")]),
    ("Veggie Stir Fry",       [("Broccoli","100g"),("Bell pepper","1"),("Carrot","1"),("Soy sauce","2 tbsp"),("Rice","100g")]),
    ("Falafel Wrap",          [("Falafel","4 pieces"),("Pita","1"),("Tzatziki","2 tbsp"),("Lettuce","20g"),("Tomato","1")]),
    ("Caprese Salad",         [("Mozzarella","100g"),("Tomato","2"),("Basil","10g"),("Olive oil","1 tbsp"),("Balsamic","1 tsp")]),
    ("Chicken Noodle Soup",   [("Chicken","150g"),("Noodles","80g"),("Carrot","1"),("Celery","1 stalk"),("Chicken stock","500ml")]),
    ("Avocado Chicken Bowl",  [("Chicken breast","150g"),("Avocado","1"),("Brown rice","100g"),("Lime","1"),("Cilantro","5g")]),
    ("Greek Salad",           [("Cucumber","1"),("Tomato","2"),("Olives","30g"),("Feta","60g"),("Red onion","1/4"),("Olive oil","1 tbsp")]),
    ("Hummus Plate",          [("Hummus","100g"),("Pita bread","2"),("Carrot sticks","60g"),("Cucumber","1/2"),("Bell pepper","1/2")]),
    ("Egg Salad Sandwich",    [("Eggs","3"),("Mayo","1 tbsp"),("Mustard","1 tsp"),("Bread","2 slices"),("Lettuce","20g")]),
    ("Minestrone",            [("Vegetables mix","200g"),("Cannellini beans","80g"),("Pasta","50g"),("Tomato paste","1 tbsp"),("Vegetable stock","500ml")]),
    ("Sushi Bowl",            [("Sushi rice","100g"),("Salmon","100g"),("Avocado","1/2"),("Cucumber","1/2"),("Soy sauce","1 tbsp"),("Sesame","1 tsp")]),
    ("Club Sandwich",         [("Bread","3 slices"),("Turkey","60g"),("Bacon","2 strips"),("Lettuce","20g"),("Tomato","1"),("Mayo","1 tbsp")]),
]

DINNERS = [
    ("Spaghetti Bolognese",   [("Spaghetti","100g"),("Ground beef","150g"),("Tomato sauce","200g"),("Onion","1"),("Garlic","2 cloves"),("Parmesan","20g")]),
    ("Grilled Salmon",        [("Salmon fillet","200g"),("Lemon","1"),("Garlic","2 cloves"),("Olive oil","1 tbsp"),("Asparagus","100g")]),
    ("Chicken Curry",         [("Chicken breast","200g"),("Coconut milk","200ml"),("Curry paste","2 tbsp"),("Onion","1"),("Rice","100g")]),
    ("Beef Steak",            [("Beef steak","200g"),("Butter","1 tbsp"),("Garlic","2 cloves"),("Rosemary","2 sprigs"),("Potatoes","200g")]),
    ("Vegetable Lasagne",     [("Lasagne sheets","6"),("Ricotta","200g"),("Spinach","100g"),("Tomato sauce","300g"),("Mozzarella","100g")]),
    ("Roast Chicken",         [("Whole chicken","1.2kg"),("Lemon","1"),("Garlic","4 cloves"),("Rosemary","3 sprigs"),("Olive oil","2 tbsp")]),
    ("Prawn Stir Fry",        [("Prawns","200g"),("Noodles","100g"),("Bok choy","100g"),("Soy sauce","2 tbsp"),("Ginger","1 tsp"),("Garlic","2 cloves")]),
    ("Mushroom Risotto",      [("Arborio rice","150g"),("Mushrooms","200g"),("Onion","1"),("White wine","50ml"),("Parmesan","30g"),("Vegetable stock","500ml")]),
    ("Lamb Chops",            [("Lamb chops","300g"),("Mint sauce","1 tbsp"),("Garlic","2 cloves"),("Rosemary","2 sprigs"),("Green beans","100g")]),
    ("Fish Tacos",            [("White fish","200g"),("Corn tortillas","3"),("Cabbage slaw","60g"),("Lime","1"),("Sour cream","2 tbsp"),("Salsa","2 tbsp")]),
    ("Chicken Tikka Masala",  [("Chicken breast","200g"),("Tikka masala sauce","200g"),("Cream","50ml"),("Rice","100g"),("Naan","1")]),
    ("Pork Tenderloin",       [("Pork tenderloin","250g"),("Apple","1"),("Mustard","1 tbsp"),("Thyme","3 sprigs"),("Sweet potato","200g")]),
    ("Veggie Burger",         [("Veggie patty","1"),("Burger bun","1"),("Lettuce","20g"),("Tomato","1"),("Avocado","1/2"),("Ketchup","1 tbsp")]),
    ("Pad Thai",              [("Rice noodles","100g"),("Tofu","100g"),("Egg","1"),("Bean sprouts","50g"),("Peanuts","20g"),("Pad Thai sauce","3 tbsp")]),
    ("Beef Tacos",            [("Ground beef","150g"),("Taco shells","3"),("Cheddar","40g"),("Lettuce","20g"),("Tomato","1"),("Sour cream","2 tbsp")]),
    ("Baked Cod",             [("Cod fillet","200g"),("Lemon","1"),("Breadcrumbs","30g"),("Parsley","5g"),("Olive oil","1 tbsp"),("Cherry tomatoes","60g")]),
    ("Eggplant Parmigiana",   [("Eggplant","1"),("Tomato sauce","200g"),("Mozzarella","100g"),("Parmesan","30g"),("Basil","5g")]),
    ("Duck Breast",           [("Duck breast","200g"),("Orange","1"),("Honey","1 tbsp"),("Thyme","2 sprigs"),("Roasted vegetables","150g")]),
    ("Shrimp Pasta",          [("Pasta","100g"),("Shrimp","150g"),("Garlic","3 cloves"),("Cherry tomatoes","80g"),("White wine","50ml"),("Parsley","5g")]),
    ("Beef Stew",             [("Beef chuck","250g"),("Potato","2"),("Carrot","2"),("Onion","1"),("Beef stock","400ml"),("Thyme","2 sprigs")]),
]

SNACKS = [
    ("Apple with Peanut Butter", [("Apple","1"),("Peanut butter","1 tbsp")]),
    ("Trail Mix",             [("Mixed nuts","30g"),("Raisins","20g"),("Dark chocolate chips","10g")]),
    ("Rice Cakes",            [("Rice cakes","2"),("Almond butter","1 tbsp"),("Banana","1/2")]),
    ("Hummus and Veggies",    [("Hummus","50g"),("Carrot sticks","60g"),("Celery","2 stalks")]),
    ("Cheese and Crackers",   [("Crackers","6"),("Cheddar","40g"),("Grapes","50g")]),
    ("Protein Bar",           [("Protein bar","1")]),
    ("Edamame",               [("Edamame","100g"),("Sea salt","pinch")]),
    ("Banana",                [("Banana","1")]),
    ("Mixed Berries",         [("Strawberries","50g"),("Blueberries","50g"),("Raspberries","30g")]),
    ("Dark Chocolate",        [("Dark chocolate","30g"),("Almonds","15g")]),
    ("Greek Yogurt",          [("Greek yogurt","150g"),("Honey","1 tsp"),("Walnuts","15g")]),
    ("Boiled Eggs",           [("Eggs","2"),("Salt","pinch"),("Paprika","pinch")]),
    ("Smoothie",              [("Banana","1"),("Spinach","30g"),("Almond milk","200ml"),("Protein powder","1 scoop")]),
    ("Popcorn",               [("Popcorn kernels","30g"),("Olive oil","1 tsp"),("Salt","pinch")]),
    ("Avocado on Crispbread", [("Crispbread","2"),("Avocado","1/2"),("Lemon","1/4"),("Salt","pinch")]),
    ("Cottage Cheese",        [("Cottage cheese","150g"),("Cucumber","1/2"),("Dill","5g")]),
    ("Dates and Almonds",     [("Dates","3"),("Almonds","20g")]),
    ("Mango Slices",          [("Mango","1/2"),("Lime","1/4"),("Chili powder","pinch")]),
    ("Pita and Tzatziki",     [("Pita","1"),("Tzatziki","50g"),("Cucumber","1/4")]),
    ("Celery with Cream Cheese",[("Celery","3 stalks"),("Cream cheese","2 tbsp"),("Raisins","10g")]),
]

def seed(db, user_id):
    meal_repo     = MealRepo(db)
    template_repo = TemplateRepo(db)

    # Clear existing test data for this user (meals named like numbers)
    with db.connect() as conn:
        conn.execute("DELETE FROM meals WHERE user_id=? AND name IN ('1','2','3','4','5')", (user_id,))
        conn.execute("DELETE FROM recipe_templates WHERE user_id=? AND name IN ('1','2','3')", (user_id,))

    from models.meal import Meal
    from models.product import Product
    from models.meal_type import MealType

    type_map = {
        "breakfast": (BREAKFASTS, MealType.BREAKFAST),
        "lunch":     (LUNCHES,    MealType.LUNCH),
        "dinner":    (DINNERS,    MealType.DINNER),
        "snack":     (SNACKS,     MealType.SNACK),
    }

    today = date.today()
    meal_count = 0
    tpl_count  = 0

    for type_name, (items, meal_type) in type_map.items():
        for i, (name, products) in enumerate(items):
            # Spread meals over the last 60 days
            meal_date = today - timedelta(days=i * 3)

            # Add as logged meal
            m = Meal(
                name=name,
                meal_type=meal_type,
                meal_date=meal_date,
                products=[Product(name=p[0], quantity=p[1]) for p in products],
                notes="",
                recipe="",
            )
            meal_repo.create(m, user_id=user_id)
            meal_count += 1

            # Also add as recipe template (so recommender uses it)
            try:
                template_repo.create({
                    "name":     name,
                    "meal_type": meal_type,
                    "notes":    "",
                    "recipe":   "",
                    "products": [{"name": p[0], "quantity": p[1]} for p in products],
                }, user_id=user_id)
                tpl_count += 1
            except Exception:
                pass  # skip if duplicate

    print(f"✔  Seeded {meal_count} meals and {tpl_count} templates for user_id={user_id}")


def test_recommender(db, user_id):
    from repo.meal_repo import MealRepo
    from repo.template_repo import TemplateRepo

    meal_repo     = MealRepo(db)
    template_repo = TemplateRepo(db)
    agent         = RecommendationAgent(meal_repo, template_repo=template_repo)

    print("\n── Day recommendation ──────────────────────────────")
    rec = agent.recommend_day(user_id=user_id)
    print(f"  Date: {rec['target_date']}")
    for slot in ("breakfast", "lunch", "dinner"):
        r = rec[slot]
        print(f"  {slot:10s}: {r['meal_name']:30s}  score={r['diversity_score']}")

    print("\n── Week recommendation (first 3 days) ──────────────")
    week = agent.recommend_week(user_id=user_id)
    for day in week["days"][:3]:
        print(f"  {day['day']:10s} ({day['date']})")
        for slot in ("breakfast", "lunch", "dinner"):
            r = day[slot]
            print(f"    {slot:10s}: {r['meal_name']:30s}  score={r['diversity_score']}")

    # Check for repeats across the week
    print("\n── Checking for repeats across week ────────────────")
    seen = []
    has_repeat = False
    for day in week["days"]:
        for slot in ("breakfast", "lunch", "dinner"):
            name = day[slot]["meal_name"]
            if name in seen:
                print(f"  ⚠  REPEAT: '{name}' on {day['date']} ({slot})")
                has_repeat = True
            seen.append(name)
    if not has_repeat:
        print("  ✔  No repeats across the week!")


if __name__ == "__main__":
    db = Database()
    seed(db, USER_ID)
    test_recommender(db, USER_ID)
