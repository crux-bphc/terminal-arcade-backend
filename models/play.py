from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from . import SQLBase


class DbPlay(SQLBase):
    game_id: Mapped[str] = mapped_column(ForeignKey("game.game_id"), primary_key=True)
    user_email: Mapped[str] = mapped_column(
        ForeignKey("user.email"), primary_key=True
    )
    __tablename__ = "plays_association_table"

    __table_args__= {'extend_existing' : True}

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
