"""Public request and response schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator


class PurchaseCreate(BaseModel):
    item_name: str = Field(min_length=1, max_length=120)
    quantity: Decimal = Field(gt=0, max_digits=12, decimal_places=3)
    unit: str = Field(min_length=1, max_length=20)
    purchased_at: datetime
    expires_at: datetime | None = None

    @field_validator("item_name")
    @classmethod
    def normalize_item_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("item_name must not be blank")
        return normalized

    @field_validator("unit")
    @classmethod
    def normalize_unit(cls, value: str) -> str:
        normalized = value.strip().casefold()
        if not normalized:
            raise ValueError("unit must not be blank")
        return normalized

    @model_validator(mode="after")
    def expiry_must_not_precede_purchase(self) -> "PurchaseCreate":
        if self.expires_at is not None and self.expires_at < self.purchased_at:
            raise ValueError("expires_at must be on or after purchased_at")
        return self


class PurchaseRead(BaseModel):
    id: int
    item_id: int
    item_name: str
    quantity: Decimal
    unit: str
    purchased_at: datetime
    expires_at: datetime | None

    model_config = {"from_attributes": True}
