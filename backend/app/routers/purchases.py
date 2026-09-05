"""Purchase logging endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Item, Purchase
from app.schemas import PurchaseCreate, PurchaseRead
from app.services.pantry import refresh_pantry_item
from app.services.reminders import build_or_update_reminder_batch


router = APIRouter(prefix="/api/v1/purchases", tags=["purchases"])


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
