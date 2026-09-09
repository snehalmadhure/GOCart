"""Virtual-pantry endpoints."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth import get_current_user
from app.models import PantryState
from app.services.pantry import refresh_all_pantry_states
from app.services.reminders import build_or_update_reminder_batch


PantryStatus = Literal["in_stock", "low", "out", "expired", "unknown"]


class PantryItemRead(BaseModel):
    item_id: int
    item_name: str
    estimated_quantity: Decimal | None
    unit: str | None
    days_left: Decimal | None
    run_out_at: datetime | None
    status: PantryStatus
    last_calculated_at: datetime


class PantryRead(BaseModel):
    items: list[PantryItemRead]


router = APIRouter(prefix="/api/v1/pantry", tags=["pantry"])


@router.get("", response_model=PantryRead)
def get_pantry(
    status: PantryStatus | Literal["all"] = "all",
    as_of: datetime | None = Query(default=None, description="Optional calculation time, useful for testing."),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> PantryRead:
    """Return freshly calculated virtual-pantry state for every known item."""

    refresh_all_pantry_states(db, user_id, as_of)
    build_or_update_reminder_batch(db, user_id, as_of)
    statement = select(PantryState).options(joinedload(PantryState.item)).where(PantryState.user_id == user_id).order_by(PantryState.item_id)
    if status != "all":
        statement = statement.where(PantryState.status == status)
    states = db.scalars(statement).all()
    return PantryRead(
        items=[
            PantryItemRead(
                item_id=state.item_id,
                item_name=state.item.name,
                estimated_quantity=state.estimated_quantity,
                unit=state.unit,
                days_left=state.estimated_days_left,
                run_out_at=state.predicted_run_out_at,
                status=state.status,
                last_calculated_at=state.last_calculated_at,
            )
            for state in states
        ]
    )
