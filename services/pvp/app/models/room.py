"""
PvP Room models.

Структура по образцу Rolls.codes:
- Комната (Room) — место где игроки ставят гифты
- Ставка (Bet) — гифт положенный в пул
- Результат (Result) — итог раунда
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import (
    String, Boolean, Integer, Numeric, DateTime,
    ForeignKey, func, Enum as SQLEnum, Text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RoomStatus(str, Enum):
    """Статус комнаты."""
    WAITING = "waiting"      # Ожидает игроков
    COUNTDOWN = "countdown"  # Обратный отсчёт до старта
    SPINNING = "spinning"    # Крутится рулетка
    FINISHED = "finished"    # Раунд завершён
    CANCELLED = "cancelled"  # Отменена (недостаточно игроков)


class RoomType(str, Enum):
    """Тип комнаты."""
    CLASSIC = "classic"      # Классика — все гифты в пул, 1 победитель
    LUCKY = "lucky"          # Lucky Roll — соло режим
    MONO = "mono"            # Mono — только одинаковые гифты


class Room(Base):
    """
    PvP комната.

    Игроки присоединяются к комнате и ставят свои гифты.
    Вес ставки = стоимость гифта в TON.
    Шанс победы пропорционален весу ставки.
    """
    __tablename__ = "pvp_rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)

    # Тип и статус
    room_type: Mapped[RoomType] = mapped_column(
        SQLEnum(RoomType),
        default=RoomType.CLASSIC
    )
    status: Mapped[RoomStatus] = mapped_column(
        SQLEnum(RoomStatus),
        default=RoomStatus.WAITING
    )

    # Настройки комнаты
    min_bet_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=1)
    max_bet_ton: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 9), nullable=True)
    max_players: Mapped[int] = mapped_column(Integer, default=10)
    countdown_seconds: Mapped[int] = mapped_column(Integer, default=30)

    # Статистика раунда
    total_pool_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=0)
    total_bets: Mapped[int] = mapped_column(Integer, default=0)
    total_players: Mapped[int] = mapped_column(Integer, default=0)

    # Победитель
    winner_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    winner_ticket: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    winning_spin_degree: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)

    # Provably Fair
    server_seed: Mapped[str] = mapped_column(String(128))
    server_seed_hash: Mapped[str] = mapped_column(String(64), index=True)
    client_seed: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    nonce: Mapped[int] = mapped_column(Integer, default=0)

    # Timing
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # House fee (процент)
    house_fee_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=5)

    # Relationships
    bets: Mapped[List["Bet"]] = relationship(
        "Bet",
        back_populates="room",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Room {self.room_code} ({self.status.value})>"


class Bet(Base):
    """
    Ставка в PvP комнате.

    Один гифт = одна ставка.
    Вес ставки = стоимость гифта в TON.
    """
    __tablename__ = "pvp_bets"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("pvp_rooms.id", ondelete="CASCADE"),
        index=True
    )

    # Игрок
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    user_telegram_id: Mapped[int] = mapped_column(Integer)
    user_name: Mapped[str] = mapped_column(String(100))
    user_avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Гифт
    gift_address: Mapped[str] = mapped_column(String(100))
    gift_name: Mapped[str] = mapped_column(String(200))
    gift_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    gift_value_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9))

    # Тикеты (для рулетки)
    # Каждый 0.01 TON = 1 тикет
    # tickets_start..tickets_end — диапазон тикетов этой ставки
    tickets_start: Mapped[int] = mapped_column(Integer)
    tickets_end: Mapped[int] = mapped_column(Integer)
    tickets_count: Mapped[int] = mapped_column(Integer)

    # Win chance (процент)
    win_chance_percent: Mapped[Decimal] = mapped_column(Numeric(10, 6))

    # Статус
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timing
    placed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    room: Mapped["Room"] = relationship("Room", back_populates="bets")

    def __repr__(self) -> str:
        return f"<Bet {self.gift_name} by user {self.user_id}>"


class UserStats(Base):
    """
    Статистика игрока в PvP.
    """
    __tablename__ = "pvp_user_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)

    # Wins/Losses
    total_wins: Mapped[int] = mapped_column(Integer, default=0)
    total_losses: Mapped[int] = mapped_column(Integer, default=0)
    total_games: Mapped[int] = mapped_column(Integer, default=0)

    # Volume
    total_wagered_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=0)
    total_won_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=0)
    total_profit_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=0)

    # Streaks
    current_win_streak: Mapped[int] = mapped_column(Integer, default=0)
    max_win_streak: Mapped[int] = mapped_column(Integer, default=0)

    # Biggest
    biggest_win_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=0)
    biggest_loss_ton: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=0)

    # Timing
    first_game_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_game_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<UserStats user={self.user_id} wins={self.total_wins}>"
