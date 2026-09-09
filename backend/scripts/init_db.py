"""Create the current GOCart schema in an empty database.

Run from the backend directory with a direct PostgreSQL connection:
    GOCART_DATABASE_URL=postgresql://... python scripts/init_db.py
"""

import argparse
from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import models  # noqa: F401 - registers all ORM tables with Base.
from sqlalchemy import text

from app.database import Base, engine


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize the GOCart schema.")
    parser.add_argument("--reset", action="store_true", help="Drop only GOCart application tables before recreating them.")
    args = parser.parse_args()

    if args.reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Supabase owns auth.users outside this application's SQLAlchemy metadata.
    # Add the cross-schema ownership constraints after the app tables exist.
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            for table in ("items", "purchases", "pantry_states", "reminder_batches", "reminder_batch_items", "shopping_lists", "shopping_list_items"):
                constraint = f"fk_{table}_user"
                connection.execute(
                    text(
                        f"ALTER TABLE {table} ADD CONSTRAINT {constraint} "
                        "FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE"
                    )
                )
    print("GOCart database schema is ready.")


if __name__ == "__main__":
    main()
