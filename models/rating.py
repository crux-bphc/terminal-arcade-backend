from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from . import SQLBase


class DbRating(SQLBase):
    game_id: Mapped[str] = mapped_column(ForeignKey("game.game_id"), primary_key=True)
    player_email: Mapped[str] = mapped_column(
        ForeignKey("user.email"), primary_key=True
    )
    rating: Mapped[int]
    __tablename__ = "rating"
