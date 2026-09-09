"""Purchase logging endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Item, Purchase
from app.schemas import PurchaseCreate, PurchaseRead
from app.services.pantry import refresh_pantry_item
from app.services.reminders import build_or_update_reminder_batch


router = APIRouter(prefix="/api/v1/purchases", tags=["purchases"])
import_router = APIRouter(prefix="/api/purchases", tags=["purchases"])


class PurchaseImportRead(BaseModel):
    found: int
    ready: int
    review: int


def _name_key(name: str) -> str:
    return name.casefold()


def _to_response(purchase: Purchase) -> PurchaseRead:
    return PurchaseRead(
        id=purchase.id,
        item_id=purchase.item_id,
        item_name=purchase.item.name,
        quantity=purchase.quantity,
        unit=purchase.unit,
        purchased_at=purchase.purchased_at,
        expires_at=purchase.expires_at,
    )


@import_router.post("/import", response_model=PurchaseImportRead)
def import_purchase_history() -> PurchaseImportRead:
    """Provide the frontend's import-status contract until a source is connected.

    The current browser request contains neither a selected file nor source
    credentials, so it cannot safely import records yet. Returning a completed
    zero-result lets the UI render its review state instead of receiving a 404.
    """

    return PurchaseImportRead(found=0, ready=0, review=0)


@router.post("", response_model=PurchaseRead, status_code=status.HTTP_201_CREATED)
def create_purchase(payload: PurchaseCreate, db: Session = Depends(get_db)) -> PurchaseRead:
    """Persist a purchase and create its canonical item when needed."""

    item = db.scalar(select(Item).where(Item.name_key == _name_key(payload.item_name)))
    if item is None:
        item = Item(name=payload.item_name, name_key=_name_key(payload.item_name), default_unit=payload.unit)
        db.add(item)
        db.flush()

    purchase = Purchase(
        item_id=item.id,
        quantity=payload.quantity,
        unit=payload.unit,
        purchased_at=payload.purchased_at,
        expires_at=payload.expires_at,
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    purchase.item = item
    refresh_pantry_item(db, item.id)
    build_or_update_reminder_batch(db)
    return _to_response(purchase)


@router.put("/{purchase_id}", response_model=PurchaseRead)
def update_purchase(purchase_id: int, payload: PurchaseCreate, db: Session = Depends(get_db)) -> PurchaseRead:
    """Update a purchase and refresh both affected pantry items."""

    purchase = db.get(Purchase, purchase_id)
    if purchase is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")
    previous_item_id = purchase.item_id
    item = db.scalar(select(Item).where(Item.name_key == _name_key(payload.item_name)))
    if item is None:
        item = Item(name=payload.item_name, name_key=_name_key(payload.item_name), default_unit=payload.unit)
        db.add(item)
        db.flush()
    purchase.item_id = item.id
    purchase.quantity = payload.quantity
    purchase.unit = payload.unit
    purchase.purchased_at = payload.purchased_at
    purchase.expires_at = payload.expires_at
    db.commit()
    db.refresh(purchase)
    purchase.item = item
    refresh_pantry_item(db, previous_item_id)
    if item.id != previous_item_id:
        refresh_pantry_item(db, item.id)
    build_or_update_reminder_batch(db)
    return _to_response(purchase)


@router.delete("/{purchase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_purchase(purchase_id: int, db: Session = Depends(get_db)) -> None:
    """Remove an incorrectly logged purchase and recalculate its pantry item."""

    purchase = db.get(Purchase, purchase_id)
    if purchase is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")
    item_id = purchase.item_id
    db.delete(purchase)
    db.commit()
    refresh_pantry_item(db, item_id)
    build_or_update_reminder_batch(db)


@router.get("", response_model=list[PurchaseRead])
def list_purchases(
    item_name: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[PurchaseRead]:
    """List purchases newest first, optionally for one case-insensitive item name."""

    statement = select(Purchase).options(joinedload(Purchase.item)).order_by(Purchase.purchased_at.desc(), Purchase.id.desc())
    if item_name is not None:
        statement = statement.join(Purchase.item).where(Item.name_key == _name_key(item_name))
    purchases = db.scalars(statement.offset(offset).limit(limit)).all()
    return [_to_response(purchase) for purchase in purchases]
