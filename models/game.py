from typing import Optional
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
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


class DbGame(SQLBase):
    title: Mapped[str]
    description: Mapped[str]
    creator_email: Mapped[str] = mapped_column(ForeignKey("user.email"))
    lb_entry: Mapped[Optional["DbLeaderboardEntry"]] = relationship(
        back_populates="game"
    )
    ratings: Mapped[List["DbRating"]] = relationship(back_populates="game")
    creator: Mapped[DbUser] = relationship(back_populates="games")
    game_id: Mapped[str] = mapped_column(
        String(GAME_ID_LEN),
        default=gen_game_id,
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    disabled: Mapped[bool] = mapped_column(default=False)
    number_of_plays: Mapped[int] = mapped_column(default=0)
    number_of_ratings: Mapped[int] = mapped_column(default=0)
    total_playtime: Mapped[int] = mapped_column(default=0)
    total_rating: Mapped[int] = mapped_column(default=0)
    __tablename__: str = "game"
