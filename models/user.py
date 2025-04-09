from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import SQLBase
from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .game import DbGame
    from .player_leaderboard import DbPlayerLeaderBoardEntry
    from .rating import DbRating


class DbUser(SQLBase):
    email: Mapped[str] = mapped_column(primary_key=True)
    games: Mapped[List["DbGame"]] = relationship(back_populates="creator")
    player_lb_entry: Mapped[Optional["DbPlayerLeaderBoardEntry"]] = relationship(
        back_populates="player"
    )
    ratings_given: Mapped[Optional["DbRating"]] = relationship(
        back_populates="rating_user"
    )
    __tablename__: str = "user"
