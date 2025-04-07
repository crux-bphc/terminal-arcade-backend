from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    sessionmaker,
)
import os

username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
db = os.getenv("POSTGRES_DB")
assert not any([e is None for e in [username, password, host, db]])

engine = create_engine(f"postgresql://{username}:{password}@{host}/{db}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class SQLBase(DeclarativeBase, MappedAsDataclass):
    pass


# ignore the linting errors from this, we need to make sure all the classes get bound to the base before doing create table, so these need to be run
from .game import DbGame
from .user import DbUser
from .rating import DbRating
from .player_leaderboard import DbPlayerLeaderBoardEntry
from .leaderboard import DbLeaderboardEntry


def create_db_and_init():
    SQLBase.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
