"""Synthetic data with known truth for evaluating consumption inference."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import json
import random

from .catalog import get_catalog_item
from .contracts import PurchaseEvent


@dataclass(frozen=True)
class SyntheticItemConfig:
    item: str
    true_days_per_unit: float
    daily_jitter: float
    reorder_point_units: float = 0.2


DEFAULT_SYNTHETIC_ITEMS = (
    SyntheticItemConfig("milk", 4.0, 0.20),
    SyntheticItemConfig("bread", 5.0, 0.18),
    SyntheticItemConfig("eggs", 7.0, 0.15),
    SyntheticItemConfig("coffee", 20.0, 0.08),
)


@dataclass(frozen=True)
class SyntheticDataset:
    events: list[PurchaseEvent]
    truth_days_per_unit: dict[str, float]

    def records(self) -> list[dict[str, object]]:
        return [event.to_dict() for event in self.events]

    def write_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.records(), indent=2), encoding="utf-8")


def generate_synthetic_history(
    *,
    total_days: int = 180,
    start_date: date = date(2026, 1, 1),
    seed: int = 42,
    skip_probability: float = 0.10,
    double_buy_probability: float = 0.15,
    configs: tuple[SyntheticItemConfig, ...] = DEFAULT_SYNTHETIC_ITEMS,
) -> SyntheticDataset:
    """Simulate noisy purchases driven by hidden consumption rates.

    Unlike a simple gap generator, this keeps a hidden inventory balance. A
    double purchase genuinely postpones the next restock event, which lets the
    evaluator test whether quantity-aware inference recovers the true cadence.
    """
    if total_days <= 0:
        raise ValueError("total_days must be positive")
    if not 0 <= skip_probability <= 1 or not 0 <= double_buy_probability <= 1:
        raise ValueError("probabilities must be between zero and one")

    events: list[PurchaseEvent] = []
    truth: dict[str, float] = {}

    for index, config in enumerate(configs):
        rng = random.Random(seed + index * 997)
        catalog_item = get_catalog_item(config.item)
        inventory = 0.0
        next_restock_attempt = 0
        truth[config.item] = config.true_days_per_unit

        for day_offset in range(total_days):
            current_day = start_date + timedelta(days=day_offset)
            needs_restock = inventory <= config.reorder_point_units
            if needs_restock and day_offset >= next_restock_attempt:
                should_skip = day_offset != 0 and rng.random() < skip_probability
                if should_skip:
                    delay = rng.randint(1, max(2, round(config.true_days_per_unit / 2)))
                    next_restock_attempt = day_offset + delay
                else:
                    quantity = 2 if rng.random() < double_buy_probability else 1
                    events.append(
                        PurchaseEvent(
                            item=config.item,
                            quantity=quantity,
                            date=current_day,
                            unit=catalog_item.unit,
                            unit_price=catalog_item.typical_price,
                            expires_in_days=catalog_item.shelf_life_days,
                        )
                    )
                    inventory += quantity
                    next_restock_attempt = day_offset + 1

            base_daily_usage = 1 / config.true_days_per_unit
            noise = rng.uniform(1 - config.daily_jitter, 1 + config.daily_jitter)
            inventory = max(0.0, inventory - base_daily_usage * noise)

    events.sort(key=lambda event: (event.date, event.item))
    return SyntheticDataset(events=events, truth_days_per_unit=truth)
