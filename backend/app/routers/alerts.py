"""Restock alert endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth import get_current_user
from app.models import ReminderBatch, ReminderBatchItem


class ReminderItemRead(BaseModel):
    item_id: int
    item_name: str
    suggested_quantity: Decimal
    reason: str


class ReminderBatchRead(BaseModel):
    id: int
    status: Literal["pending", "snoozed", "dismissed"]
    scheduled_for: datetime
    items: list[ReminderItemRead]


router = APIRouter(prefix="/api/v1/restock-alerts", tags=["restock alerts"])


class SnoozeRequest(BaseModel):
    days: int = Field(ge=1, le=30)


def _to_response(batch: ReminderBatch) -> ReminderBatchRead:
    return ReminderBatchRead(
        id=batch.id,
        status=batch.status,
        scheduled_for=batch.scheduled_for,
        items=[
            ReminderItemRead(
                item_id=entry.item_id,
                item_name=entry.item.name,
                suggested_quantity=entry.suggested_quantity,
                reason=entry.reason,
            )
            for entry in batch.items
        ],
    )


@router.get("", response_model=list[ReminderBatchRead])
def list_restock_alerts(
    include_dismissed: bool = False,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> list[ReminderBatchRead]:
    """Return grouped reminders created during pantry refreshes."""
    statement = select(ReminderBatch).options(
        joinedload(ReminderBatch.items).joinedload(ReminderBatchItem.item)
    ).where(ReminderBatch.user_id == user_id).order_by(ReminderBatch.created_at.desc(), ReminderBatch.id.desc())
    if not include_dismissed:
        statement = statement.where(ReminderBatch.status.in_(["pending", "snoozed"]))
    batches = db.execute(statement).unique().scalars().all()
    return [_to_response(batch) for batch in batches]


@router.post("/{batch_id}/dismiss", response_model=ReminderBatchRead)
def dismiss_restock_alert(batch_id: int, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)) -> ReminderBatchRead:
    """Dismiss one pending reminder batch without deleting its audit trail."""

    batch = db.scalar(
        select(ReminderBatch)
        .options(joinedload(ReminderBatch.items).joinedload(ReminderBatchItem.item))
        .where(ReminderBatch.id == batch_id, ReminderBatch.user_id == user_id)
    )
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder batch not found")
    if batch.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reminder batch is not pending")
    batch.status = "dismissed"
    batch.dismissed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(batch)
    return _to_response(batch)


@router.post("/{batch_id}/snooze", response_model=ReminderBatchRead)
def snooze_restock_alert(batch_id: int, payload: SnoozeRequest, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)) -> ReminderBatchRead:
    """Postpone a reminder while retaining the batched items."""

    batch = db.scalar(
        select(ReminderBatch)
        .options(joinedload(ReminderBatch.items).joinedload(ReminderBatchItem.item))
        .where(ReminderBatch.id == batch_id, ReminderBatch.user_id == user_id)
    )
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder batch not found")
    if batch.status not in {"pending", "snoozed"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reminder batch cannot be snoozed")
    batch.status = "snoozed"
    batch.scheduled_for = datetime.now(timezone.utc) + timedelta(days=payload.days)
    db.commit()
    db.refresh(batch)
    return _to_response(batch)
