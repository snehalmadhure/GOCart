"""Pantry-aware, AI-generated shopping-list endpoint."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import PantryState
from app.services.pantry import LOW_STOCK_DAYS, refresh_all_pantry_states
from app.services.prediction import generate_list


class ShoppingListGenerateRequest(BaseModel):
    intent: str = Field(min_length=3, max_length=500)


class ShoppingListItemRead(BaseModel):
    item_name: str
    quantity: Decimal
    unit: str
    reason: str
    pantry_warning: str | None = None


class ShoppingListRead(BaseModel):
    intent: str
    items: list[ShoppingListItemRead]


router = APIRouter(prefix="/api/v1/shopping-lists", tags=["shopping lists"])


@router.post("/generate", response_model=ShoppingListRead)
def generate_shopping_list(
    payload: ShoppingListGenerateRequest,
    db: Session = Depends(get_db),
) -> ShoppingListRead:
    """Generate suggestions and warn when a non-low pantry item already exists."""

    refresh_all_pantry_states(db)
    states = db.scalars(select(PantryState).options(joinedload(PantryState.item))).all()
    well_stocked = {
        state.item.name.casefold()
        for state in states
        if state.status == "in_stock"
        and state.estimated_days_left is not None
        and state.estimated_days_left > LOW_STOCK_DAYS
    }
    suggestions = generate_list(payload.intent, states)
    return ShoppingListRead(
        intent=payload.intent,
        items=[
            ShoppingListItemRead(
                item_name=suggestion.item_name,
                quantity=suggestion.quantity,
                unit=suggestion.unit,
                reason=suggestion.reason,
                pantry_warning=suggestion.pantry_warning
                or (
                    "Already sufficiently stocked in your pantry — still add it?"
                    if suggestion.item_name.casefold() in well_stocked
                    else None
                ),
            )
            for suggestion in suggestions
        ],
    )
