from typing import Optional, Set
from sqlalchemy import DateTime, ForeignKey, String, Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime

from . import SQLBase

from string import ascii_letters, digits
from random import choices

from .user import DbUser

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .leaderboard import DbLeaderboardEntry
    from .rating import DbRating


chars = ascii_letters + digits
GAME_ID_LEN = 20


def gen_game_id():
    return "".join(choices(chars, k=GAME_ID_LEN))


plays_association_table = Table(
    "plays_association_table",
    SQLBase.metadata,
    Column("user_email", ForeignKey("user.email"), primary_key=True),
    Column("game_id", ForeignKey("game.game_id"), primary_key=True),
)


class DbGame(SQLBase):
    title: Mapped[str]
    description: Mapped[str]
    file: Mapped[str]
    game_id: Mapped[str] = mapped_column(
        String(GAME_ID_LEN),
        default=gen_game_id,
        primary_key=True,
    )
    creator_email: Mapped[str] = mapped_column(ForeignKey("user.email"))
    lb_entry: Mapped[Optional["DbLeaderboardEntry"]] = relationship(
        back_populates="game"
    )
    played_users: Mapped[List[DbUser]] = relationship(
        back_populates="played_games",
        secondary=plays_association_table,
    )
    ratings: Mapped[List["DbRating"]] = relationship(back_populates="game")
    creator: Mapped[DbUser] = relationship(back_populates="games")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    disabled: Mapped[bool] = mapped_column(default=False)
    number_of_plays: Mapped[int] = mapped_column(default=0)
    number_of_ratings: Mapped[int] = mapped_column(default=0)
    total_playtime: Mapped[int] = mapped_column(default=0)
    total_rating: Mapped[int] = mapped_column(default=0)
    __tablename__: str = "game"

    def add_played_user(self, user_email: str):
        return insert(plays_association_table).values(
            user_email=user_email, game_id=self.game_id
        ).on_conflict_do_nothing()

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
