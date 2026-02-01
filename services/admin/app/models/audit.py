"""
Audit Log - логирование всех действий админа

Важно для безопасности и отслеживания:
- Кто изменил настройки
- Когда было изменение
- Что именно поменялось
"""
from sqlalchemy import Column, Integer, String, JSON, DateTime, func, Enum as SQLEnum
from enum import Enum
from .base import Base


class AuditAction(str, Enum):
    """Типы действий для аудита"""
    # Настройки игр
    GAME_SETTINGS_UPDATE = "game_settings_update"
    GAME_SETTINGS_CREATE = "game_settings_create"

    # Таргетирование
    USER_TARGET_CREATE = "user_target_create"
    USER_TARGET_UPDATE = "user_target_update"
    USER_TARGET_DELETE = "user_target_delete"

    # Раунды
    ROUND_OVERRIDE_CREATE = "round_override_create"
    ROUND_OVERRIDE_DELETE = "round_override_delete"
    ROUND_OVERRIDE_USED = "round_override_used"

    # Экстренные действия
    GAME_DISABLE = "game_disable"
    GAME_ENABLE = "game_enable"
    EMERGENCY_STOP = "emergency_stop"

    # Баланс/выплаты
    MANUAL_PAYOUT = "manual_payout"
    BALANCE_ADJUSTMENT = "balance_adjustment"


class AuditLog(Base):
    """
    Лог аудита - записи всех админских действий
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Когда
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)

    # Кто (админ)
    admin_id = Column(String(100), nullable=False, index=True)
    admin_username = Column(String(100), nullable=True)
    admin_ip = Column(String(50), nullable=True)

    # Что
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    action_description = Column(String(500), nullable=True)

    # Детали изменения
    entity_type = Column(String(50), nullable=True)  # game_settings, user_target, etc.
    entity_id = Column(String(100), nullable=True)

    # Значения до и после (для отката)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)

    # Дополнительный контекст
    metadata = Column(JSON, nullable=True)
