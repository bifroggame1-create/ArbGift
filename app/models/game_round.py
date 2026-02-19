from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GameRound(Base):
    __tablename__ = "game_rounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_type: Mapped[str] = mapped_column(String(32), index=True)
    round_id: Mapped[str] = mapped_column(String(64), unique=True)
    server_seed_hash: Mapped[str] = mapped_column(String(128))
    server_seed: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
