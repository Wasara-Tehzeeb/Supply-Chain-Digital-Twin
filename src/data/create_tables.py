from src.data.database import engine
from src.data.models import Base


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("All database tables are ready!")


if __name__ == "__main__":
    create_tables()
