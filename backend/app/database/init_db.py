from app.database.database import Base, engine
from app.database import models  # noqa: F401


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    initialize_database()
    print("SmartFarm database initialized")