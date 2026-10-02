"""
Meal Manager — stdlib-only entry point.
No external packages required. Runs on Python 3.8+.

Usage:
    python3.11 main.py [--seed] [--charts] [--host HOST] [--port PORT]

Flags:
    --seed      Populate DB with 14 days of sample data (idempotent).
    --charts    Print terminal visualisations then exit.
    --host      Bind host (default: 0.0.0.0).
    --port      Bind port (default: 8000).
"""

import argparse
import sys
from http.server import HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from repo.database import Database
from repo.meal_repo import MealRepo
from repo.template_repo import TemplateRepo
from repo.shopping_repo import ShoppingRepo
from repo.weekly_menu_repo import WeeklyMenuRepo
from repo.recommendation_settings_repo import RecommendationSettingsRepo
from repo.fridge_repo import FridgeRepo
from repo.ingredient_repo import IngredientRepo
from services.meal_service import MealService
from services.recommendation_agent import RecommendationAgent
from services.auth_service import AuthService
from services.family_service import FamilyService
from rest.router import MealRouter


def build_handler(
    meal_service:     MealService,
    agent:            RecommendationAgent,
    template_repo:    TemplateRepo,
    shopping_repo:    ShoppingRepo,
    weekly_menu_repo: WeeklyMenuRepo,
    auth_service:     AuthService,
    family_service:   FamilyService,
    rec_settings_repo: RecommendationSettingsRepo,
    fridge_repo:       FridgeRepo,
    ingredient_repo:   IngredientRepo,
):
    class Handler(MealRouter):
        pass
    Handler.meal_service      = meal_service
    Handler.agent             = agent
    Handler.template_repo     = template_repo
    Handler.shopping_repo     = shopping_repo
    Handler.weekly_menu_repo  = weekly_menu_repo
    Handler.auth_service      = auth_service
    Handler.family_service    = family_service
    Handler.rec_settings_repo = rec_settings_repo
    Handler.fridge_repo       = fridge_repo
    Handler.ingredient_repo   = ingredient_repo
    return Handler


def run_seed(repo: MealRepo) -> None:
    from utils.data_generator import DataGenerator
    n = DataGenerator(repo).seed(days=14)
    print(f"✔  Seeded {n} sample meals.")


def run_charts(repo: MealRepo) -> None:
    from utils.visualizer import Visualizer
    meals = repo.get_recent(days=14)
    if not meals:
        print("⚠  No meals found — run with --seed first or add some via the API.")
        return
    Visualizer(meals).print_all()


def main() -> None:
    parser = argparse.ArgumentParser(description="Meal Manager (stdlib-only)")
    parser.add_argument("--seed",   action="store_true", help="Seed 14 days of sample data")
    parser.add_argument("--charts", action="store_true", help="Print terminal visualisations and exit")
    parser.add_argument("--host",   default="0.0.0.0",   help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port",   type=int, default=8000, help="Bind port (default: 8000)")
    args = parser.parse_args()

    db                = Database()
    repo              = MealRepo(db)
    template_repo     = TemplateRepo(db)
    shopping_repo     = ShoppingRepo(db)
    weekly_menu_repo  = WeeklyMenuRepo(db)
    auth_service      = AuthService(db)
    family_service    = FamilyService(db)
    rec_settings_repo = RecommendationSettingsRepo(db)
    fridge_repo       = FridgeRepo(db)
    ingredient_repo   = IngredientRepo(db)
    svc               = MealService(repo)
    agent             = RecommendationAgent(repo, template_repo=template_repo)

    if args.seed:
        run_seed(repo)

    if args.charts:
        run_charts(repo)
        if not args.seed:
            return

    handler = build_handler(svc, agent, template_repo, shopping_repo,
                            weekly_menu_repo, auth_service, family_service, rec_settings_repo,
                            fridge_repo, ingredient_repo)

    port   = args.port
    server = None
    for attempt in range(10):
        try:
            server = HTTPServer((args.host, port), handler)
            break
        except OSError:
            print(f"  Port {port} in use, trying {port + 1}...")
            port += 1
    if server is None:
        print(f"  Could not bind to any port in {args.port}–{port - 1}. Exiting.")
        sys.exit(1)

    display_host = "127.0.0.1" if args.host in ("0.0.0.0", "") else args.host
    print(f"\n  Meal Manager is running!")
    print(f"  Local:   http://127.0.0.1:{port}/ui")
    print(f"  Local test:   http://0.0.0.0:{port}/ui")
    print(f"  Network: http://10.6.150.107:{port}/ui\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
