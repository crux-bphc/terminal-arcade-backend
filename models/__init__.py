from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
import os

username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
db = os.getenv("POSTGRES_DB")
assert not any([e is None for e in [username, password, host, db]])

engine = create_async_engine(
    f"postgresql+asyncpg://{username}:{password}@{host}/{db}", future=True, echo=True
)
session_maker = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


class SQLBase(DeclarativeBase):
    pass


# ignore the linting errors from this, we need to make sure all the classes get bound to the base before doing create table, so these need to be run
from .game import DbGame
from .user import DbUser
from .rating import DbRating
from .player_leaderboard import DbPlayerLeaderBoardEntry
from .leaderboard import DbLeaderboardEntry
import models.play


async def create_db_and_init():
    async with engine.begin() as conn:
        await conn.run_sync(SQLBase.metadata.create_all)


async def get_db():
    async with session_maker() as session:
        async with session.begin():
            yield session
