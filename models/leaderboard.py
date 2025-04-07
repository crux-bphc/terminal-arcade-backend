from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import mapped_column, relationship, Mapped
from datetime import datetime
from .game import DbGame
from . import SQLBase


class DbLeaderboardEntry(SQLBase):
    game_id: Mapped[str] = mapped_column(ForeignKey("game.game_id"), primary_key=True)
    score: Mapped[int]
    updated_at: Mapped[datetime]
    game: Mapped[DbGame] = relationship(back_populates="lb_entry")
    __tablename__: str = "leaderboard"
    __table_args__ = (Index("ix_game_score_updated", "score", "updated_at"),)
