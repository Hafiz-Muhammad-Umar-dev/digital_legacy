
from app.database import Base, engine
from app.models import Persona, Memory, Conversation


def main():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

    for table_name in Base.metadata.tables:
        print(f"- {table_name}")


if __name__ == "__main__":
    main()
