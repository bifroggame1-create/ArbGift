from __future__ import annotations

import json
import hashlib
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ledger import BalanceOperation, OperationType, OperationStatus
from app.models.user import User


def hash_payload(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


async def get_or_create_op(
    session: AsyncSession,
    user_id: int,
    operation_id: Optional[str],
    op_type: OperationType,
    payload: dict,
) -> Optional[BalanceOperation]:
    if not operation_id:
        return None
    existing = await session.execute(
        select(BalanceOperation).where(BalanceOperation.operation_id == operation_id)
    )
    op = existing.scalar_one_or_none()
    if op:
        return op
    op = BalanceOperation(
        operation_id=operation_id,
        user_id=user_id,
        op_type=op_type,
        status=OperationStatus.PENDING,
        request_hash=hash_payload(payload),
    )
    session.add(op)
    await session.flush()
    return op


async def lock_user(session: AsyncSession, user: User) -> User:
    result = await session.execute(
        select(User).where(User.id == user.id).with_for_update()
    )
    locked = result.scalar_one()
    return locked


def ensure_idempotent(op: Optional[BalanceOperation], payload: dict):
    if not op:
        return
    if op.status == OperationStatus.APPLIED and op.response_json:
        raise HTTPException(status_code=208, detail=op.response_json)
    if op.status == OperationStatus.PENDING and op.response_json is None and op.request_hash != hash_payload(payload):
        raise HTTPException(status_code=409, detail="Idempotency key reused with different payload")
