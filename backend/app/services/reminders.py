"""Rules for grouping low-stock pantry items into one reminder."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PantryState, ReminderBatch, ReminderBatchItem


URGENT_DAYS = Decimal("3")


def build_or_update_reminder_batch(db: Session, user_id: str, as_of: datetime | None = None) -> ReminderBatch | None:
    """Create or update the one pending batch for urgent restock needs.

    The actual notification provider is deliberately outside this service. It
    can later deliver a pending batch at ``scheduled_for``.
    """

    now = as_of or datetime.now(timezone.utc)
    urgent_states = db.scalars(
        select(PantryState).where(
            PantryState.user_id == user_id,
            (PantryState.status.in_(["low", "out", "expired"]))
            | (PantryState.estimated_days_left <= URGENT_DAYS)
        )
    ).all()
    if not urgent_states:
        return None

    batch = db.scalar(
        select(ReminderBatch)
        .where(ReminderBatch.user_id == user_id, ReminderBatch.status == "pending")
        .order_by(ReminderBatch.created_at.desc(), ReminderBatch.id.desc())
        .limit(1)
    )
    run_out_times = [state.predicted_run_out_at for state in urgent_states if state.predicted_run_out_at is not None]
    scheduled_for = min(run_out_times, default=now)
    if batch is None:
        batch = ReminderBatch(user_id=user_id, status="pending", scheduled_for=scheduled_for)
        db.add(batch)
        db.flush()
    else:
        batch.scheduled_for = min(batch.scheduled_for, scheduled_for)

    existing_item_ids = {item.item_id for item in batch.items}
    for state in urgent_states:
        if state.item_id in existing_item_ids:
            continue
        reason = "expired" if state.status == "expired" else f"{state.status} stock"
        batch.items.append(
            ReminderBatchItem(
                user_id=user_id,
                item_id=state.item_id,
                suggested_quantity=Decimal("1"),
                reason=reason,
            )
        )
    db.commit()
    db.refresh(batch)
    return batch
