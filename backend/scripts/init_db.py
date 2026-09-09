"""Create the current GOCart schema in an empty database.

Run from the backend directory with a direct PostgreSQL connection:
    GOCART_DATABASE_URL=postgresql://... python scripts/init_db.py
"""

from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import models  # noqa: F401 - registers all ORM tables with Base.
from app.database import Base, engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("GOCart database schema is ready.")


if __name__ == "__main__":
    main()
