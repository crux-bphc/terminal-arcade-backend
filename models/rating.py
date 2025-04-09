from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.game import DbGame
from models.user import DbUser
from . import SQLBase


class DbRating(SQLBase):
    game_id: Mapped[str] = mapped_column(ForeignKey("game.game_id"), primary_key=True)
    player_email: Mapped[str] = mapped_column(
        ForeignKey("user.email"), primary_key=True
    )
    rating: Mapped[int]
    game: Mapped[DbGame] = relationship(back_populates="ratings")
    rating_user: Mapped[DbUser] = relationship(back_populates="ratings_given")
    __tablename__ = "rating"
