from app.db import Base, engine
from app.models import Price

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created.")