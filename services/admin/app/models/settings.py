"""
Модели настроек для Gambling Admin Panel

Полный контроль над:
- RTP (Return to Player) для каждой игры
- House Edge (преимущество казино)
- Диапазоны множителей
- Таргетирование пользователей
- Ручное управление раундами
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, Enum as SQLEnum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from enum import Enum
from .base import Base, TimestampMixin


class GameType(str, Enum):
    """Типы игр"""
    PLINKO = "plinko"
    TRADING = "trading"  # Crash
    ROULETTE = "roulette"
    AVIATOR = "aviator"
    PVP = "pvp"
    UPGRADE = "upgrade"
    LUCKY = "lucky"
    GONKA = "gonka"
    BALL_ESCAPE = "ball_escape"
    ROCKET = "rocket"


class TargetMode(str, Enum):
    """Режимы таргетирования"""
    NONE = "none"           # Обычный режим
    WIN = "win"             # Принудительный выигрыш
    LOSE = "lose"           # Принудительный проигрыш
    SPECIFIC = "specific"   # Конкретный множитель/результат


class GameSettings(Base, TimestampMixin):
    """
    Настройки игры - глобальные параметры для каждого типа игры

    Используется для управления:
    - RTP (ожидаемый возврат игроку)
    - House Edge (преимущество дома)
    - Диапазоны выплат
    - Частоты выигрышей
    """
    __tablename__ = "game_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_type = Column(SQLEnum(GameType), unique=True, nullable=False, index=True)

    # Основные параметры
    is_enabled = Column(Boolean, default=True, nullable=False)
    rtp_percent = Column(Float, default=97.0, nullable=False)  # 97% RTP = 3% house edge
    house_edge_percent = Column(Float, default=3.0, nullable=False)

    # Диапазоны множителей
    min_multiplier = Column(Float, default=1.0, nullable=False)
    max_multiplier = Column(Float, default=100.0, nullable=False)

    # Частота крупных выигрышей
    big_win_threshold = Column(Float, default=5.0)  # Что считать крупным выигрышем
    big_win_frequency = Column(Float, default=0.05)  # 5% шанс крупного выигрыша

    # Специфичные настройки (JSON для гибкости)
    # Пример: {"crash_speed": 1.5, "min_crash_point": 1.2}
    custom_settings = Column(JSON, default=dict)

    # Лимиты ставок
    min_bet = Column(Float, default=0.1)
    max_bet = Column(Float, default=100.0)

    # Глобальный режим "подкрутки"
    rigged_mode = Column(Boolean, default=False)
    rigged_win_rate = Column(Float, default=0.3)  # 30% выигрышей в режиме подкрутки


class UserTarget(Base, TimestampMixin):
    """
    Таргетирование пользователей

    Позволяет настроить индивидуальное поведение для конкретных пользователей:
    - Принудительный выигрыш/проигрыш
    - Измененный RTP
    - Конкретные результаты
    """
    __tablename__ = "user_targets"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Идентификация пользователя
    user_id = Column(String(100), nullable=False, index=True)  # Telegram ID
    username = Column(String(100), nullable=True)

    # Игра (опционально - если NULL, применяется ко всем играм)
    game_type = Column(SQLEnum(GameType), nullable=True)

    # Режим таргетирования
    target_mode = Column(SQLEnum(TargetMode), default=TargetMode.NONE, nullable=False)

    # Параметры для режима SPECIFIC
    forced_multiplier = Column(Float, nullable=True)  # Принудительный множитель
    forced_result = Column(JSON, nullable=True)  # Принудительный результат (JSON)

    # Измененный RTP для пользователя
    custom_rtp = Column(Float, nullable=True)  # Если указано, переопределяет глобальный

    # Счетчик применений
    uses_remaining = Column(Integer, default=1)  # -1 = бесконечно
    uses_total = Column(Integer, default=0)

    # Период действия
    active_from = Column(DateTime, nullable=True)
    active_until = Column(DateTime, nullable=True)

    # Статус
    is_active = Column(Boolean, default=True, nullable=False)

    # Причина/комментарий от админа
    admin_note = Column(String(500), nullable=True)


class RoundOverride(Base, TimestampMixin):
    """
    Ручное управление конкретными раундами

    Позволяет админу заранее задать результат следующего раунда
    или определенного раунда по номеру.
    """
    __tablename__ = "round_overrides"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Игра
    game_type = Column(SQLEnum(GameType), nullable=False, index=True)

    # Номер раунда (опционально - если NULL, применяется к следующему)
    round_number = Column(Integer, nullable=True)

    # Принудительный результат
    forced_crash_point = Column(Float, nullable=True)  # Для Trading/Crash
    forced_slot = Column(Integer, nullable=True)  # Для Plinko
    forced_result = Column(JSON, nullable=True)  # Универсальный JSON результат

    # Таргетированный пользователь (опционально)
    target_user_id = Column(String(100), nullable=True)
    target_mode = Column(SQLEnum(TargetMode), nullable=True)

    # Статус
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)

    # Админ комментарий
    admin_note = Column(String(500), nullable=True)
    created_by = Column(String(100), nullable=True)  # Admin ID


class GameStatistics(Base, TimestampMixin):
    """
    Статистика игр для аналитики
    """
    __tablename__ = "game_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_type = Column(SQLEnum(GameType), nullable=False, index=True)

    # Период (день)
    date = Column(DateTime, nullable=False, index=True)

    # Объемы
    total_bets = Column(Integer, default=0)
    total_bet_amount = Column(Float, default=0.0)
    total_payouts = Column(Float, default=0.0)

    # Profit/Loss
    house_profit = Column(Float, default=0.0)
    actual_rtp = Column(Float, default=0.0)  # Реальный RTP за день

    # Пользователи
    unique_players = Column(Integer, default=0)
    new_players = Column(Integer, default=0)

    # Крупные события
    biggest_win = Column(Float, default=0.0)
    biggest_loss = Column(Float, default=0.0)
