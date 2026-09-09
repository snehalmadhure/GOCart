"""Pantry-aware, AI-generated shopping-list endpoint."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth import get_current_user
from app.models import PantryState, ShoppingList, ShoppingListItem
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
    id: int
    intent: str
    status: str
    items: list[ShoppingListItemRead]


router = APIRouter(prefix="/api/v1/shopping-lists", tags=["shopping lists"])


def _to_response(shopping_list: ShoppingList) -> ShoppingListRead:
    return ShoppingListRead(
        id=shopping_list.id,
        intent=shopping_list.intent,
        status=shopping_list.status,
        items=[
            ShoppingListItemRead(
                item_name=item.item_name,
                quantity=item.quantity,
                unit=item.unit,
                reason=item.reason,
                pantry_warning=item.pantry_warning,
            )
            for item in shopping_list.items
        ],
    )


@router.post("/generate", response_model=ShoppingListRead)
def generate_shopping_list(
    payload: ShoppingListGenerateRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> ShoppingListRead:
    """Generate suggestions and warn when a non-low pantry item already exists."""

    refresh_all_pantry_states(db, user_id)
    states = db.scalars(
        select(PantryState).options(joinedload(PantryState.item)).where(PantryState.user_id == user_id)
    ).all()
    well_stocked = {
        state.item.name.casefold()
        for state in states
        if state.status == "in_stock"
        and state.estimated_days_left is not None
        and state.estimated_days_left > LOW_STOCK_DAYS
    }
    suggestions = generate_list(payload.intent, states)
    shopping_list = ShoppingList(user_id=user_id, intent=payload.intent)
    db.add(shopping_list)
    for suggestion in suggestions:
        warning = suggestion.pantry_warning or (
            "Already sufficiently stocked in your pantry — still add it?"
            if suggestion.item_name.casefold() in well_stocked
            else None
        )
        shopping_list.items.append(
            ShoppingListItem(
                user_id=user_id,
                item_name=suggestion.item_name,
                quantity=suggestion.quantity,
                unit=suggestion.unit,
                reason=suggestion.reason,
                pantry_warning=warning,
            )
        )
    db.commit()
    db.refresh(shopping_list)
    return _to_response(shopping_list)


@router.post("/{shopping_list_id}/confirm", response_model=ShoppingListRead)
def confirm_shopping_list(
    shopping_list_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> ShoppingListRead:
    """Confirm a generated list without allowing another user's list to be changed."""

    shopping_list = db.scalar(
        select(ShoppingList)
        .options(joinedload(ShoppingList.items))
        .where(ShoppingList.id == shopping_list_id, ShoppingList.user_id == user_id)
    )
    if shopping_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")
    shopping_list.status = "confirmed"
    shopping_list.confirmed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(shopping_list)
    return _to_response(shopping_list)
