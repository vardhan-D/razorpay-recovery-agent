from app.database import engine
from app.db_models import Base


def init_db():
    Base.metadata.create_all(
        bind=engine
    )