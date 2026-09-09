"""Virtual-pantry state calculation and refresh."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import PantryState, Purchase
from app.services.prediction import estimate_consumption


LOW_STOCK_DAYS = 2
logger = logging.getLogger(__name__)


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def refresh_pantry_item(db: Session, user_id: str, item_id: int, as_of: datetime | None = None) -> PantryState:
    """Calculate and persist a fresh inventory state for one item."""

    calculated_at = _as_utc(as_of or datetime.now(timezone.utc))
    purchases = db.scalars(
        select(Purchase).where(Purchase.user_id == user_id, Purchase.item_id == item_id).order_by(Purchase.purchased_at)
    ).all()
    state = db.get(PantryState, {"user_id": user_id, "item_id": item_id})
    is_new_state = state is None
    if state is None:
        state = PantryState(user_id=user_id, item_id=item_id, status="unknown", last_calculated_at=calculated_at)
        db.add(state)

    # A newer refill replaces the older stock for this first-pass inventory
    # model, so only the newest purchase's expiry can make the current state
    # expired. Batch-level expiry tracking can be introduced later if needed.
    latest_expiry = _as_utc(purchases[-1].expires_at) if purchases and purchases[-1].expires_at else None
    if latest_expiry is not None and latest_expiry <= calculated_at:
        state.estimated_quantity = Decimal("0")
        state.unit = purchases[-1].unit if purchases else None
        state.estimated_days_left = Decimal("0")
        state.predicted_run_out_at = latest_expiry
        state.status = "expired"
    else:
        try:
            estimate = estimate_consumption(purchases, calculated_at)
        except Exception:  # noqa: BLE001 - ML adapter failures must not corrupt pantry state.
            logger.exception("Consumption prediction failed for item_id=%s", item_id)
            if not is_new_state:
                return state
            state.status = "unknown"
            state.last_calculated_at = calculated_at
            db.commit()
            db.refresh(state)
            return state
        state.estimated_quantity = estimate.estimated_quantity
        state.unit = purchases[-1].unit if purchases else None
        state.estimated_days_left = estimate.days_left
        state.predicted_run_out_at = estimate.run_out_at
        if estimate.confidence == "insufficient_history":
            state.status = "unknown"
        elif estimate.days_left is not None and estimate.days_left <= 0:
            state.status = "out"
        elif estimate.days_left is not None and estimate.days_left <= LOW_STOCK_DAYS:
            state.status = "low"
        else:
            state.status = "in_stock"

    state.last_calculated_at = calculated_at
    db.commit()
    db.refresh(state)
    return state


def refresh_all_pantry_states(db: Session, user_id: str, as_of: datetime | None = None) -> list[PantryState]:
    """Refresh every tracked item and return the resulting states."""

    item_ids = db.scalars(select(Purchase.item_id).where(Purchase.user_id == user_id).distinct()).all()
    return [refresh_pantry_item(db, user_id, item_id, as_of) for item_id in item_ids]
