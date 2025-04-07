from datetime import datetime

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import DbUser
from . import SQLBase


class DbPlayerLeaderBoardEntry(SQLBase):
    player_email: Mapped[str] = mapped_column(
        ForeignKey("user.email"), primary_key=True
    )
    score: Mapped[int]
    updated_at: Mapped[datetime]
    player: Mapped[DbUser] = relationship(back_populates="user.player_lb_entry")
    __tablename__ = "player_leaderboard"
    __table_args__ = (Index("ix_player_score_updated", "score", "updated_at"),)
