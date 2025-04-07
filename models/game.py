from typing import Optional
from sqlalchemy import CHAR, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from . import SQLBase

from string import ascii_letters, digits
from random import choices

from .user import DbUser

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .leaderboard import DbLeaderboardEntry


chars = ascii_letters + digits


def gen_game_id():
    return "".join(choices(chars, k=6))


class DbGame(SQLBase):
    title: Mapped[str]
    creator_email: Mapped[str] = mapped_column(ForeignKey("user.email"))
    lb_entry: Mapped[Optional["DbLeaderboardEntry"]] = relationship(
        back_populates="game"
    )
    creator: Mapped[DbUser] = relationship(back_populates="games")
    game_id: Mapped[str] = mapped_column(
        CHAR(20), default_factory=gen_game_id, primary_key=True
    )  # this needs to be default none because its auto generated
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default_factory=datetime.now
    )
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    number_of_plays: Mapped[int] = mapped_column(Integer, default=0)
    number_of_ratings: Mapped[int] = mapped_column(Integer, default=0)
    total_playtime: Mapped[int] = mapped_column(Integer, default=0)
    total_rating: Mapped[int] = mapped_column(Integer, default=0)
    __tablename__: str = "game"
