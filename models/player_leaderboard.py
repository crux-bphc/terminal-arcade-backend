from datetime import datetime

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import DbUser
from . import SQLBase


class DbPlayerLeaderBoardEntry(SQLBase):
    player_email: Mapped[str] = mapped_column(
        ForeignKey("user.email"), primary_key=True
    )
    player: Mapped[DbUser] = relationship(back_populates="player_lb_entry")
    score: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )
    __tablename__ = "player_leaderboard"
    __table_args__ = (Index("ix_player_score_updated", score.desc(), score.desc()),)
