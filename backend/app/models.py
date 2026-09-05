"""Persistent database models for GOCart."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Item(Base):
    """A canonical pantry item, identified by a normalized name."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    name_key: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    default_unit: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    purchases: Mapped[list["Purchase"]] = relationship(back_populates="item")


class Purchase(Base):
    """An immutable record of a pantry purchase."""

    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    item: Mapped[Item] = relationship(back_populates="purchases")


class PantryState(Base):
    """Cached current inventory estimate for one item."""

    __tablename__ = "pantry_states"

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    estimated_quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estimated_days_left: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    predicted_run_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="unknown")
    last_calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    item: Mapped[Item] = relationship()


class ReminderBatch(Base):
    """A single, grouped restock reminder awaiting user action."""

    __tablename__ = "reminder_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="pending")
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estimated_cart_total: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    items: Mapped[list["ReminderBatchItem"]] = relationship(back_populates="batch", cascade="all, delete-orphan")


class ReminderBatchItem(Base):
    """An item included in a grouped restock reminder."""

    __tablename__ = "reminder_batch_items"
    __table_args__ = (UniqueConstraint("batch_id", "item_id", name="uq_reminder_batch_item"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("reminder_batches.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    suggested_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    reason: Mapped[str] = mapped_column(String(120), nullable=False)

    batch: Mapped[ReminderBatch] = relationship(back_populates="items")
    item: Mapped[Item] = relationship()
