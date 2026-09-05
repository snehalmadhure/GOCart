"""A small catalog used only for defaults and recommendation quality."""

from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import normalize_item


@dataclass(frozen=True)
class CatalogItem:
    item: str
    unit: str = "unit"
    typical_price: float | None = None
    low_stock_days: float = 3.0
    shelf_life_days: int | None = None
    category: str = "other"


CATALOG: dict[str, CatalogItem] = {
    "milk": CatalogItem("milk", "carton", 68, 2.0, 5, "dairy"),
    "bread": CatalogItem("bread", "loaf", 45, 2.0, 4, "bakery"),
    "eggs": CatalogItem("eggs", "dozen", 90, 4.0, 14, "dairy"),
    "coffee": CatalogItem("coffee", "pack", 280, 7.0, None, "pantry"),
    "pasta": CatalogItem("pasta", "pack", 120, 7.0, None, "pantry"),
    "tomato sauce": CatalogItem("tomato sauce", "jar", 95, 7.0, 14, "pantry"),
    "cheese": CatalogItem("cheese", "pack", 150, 4.0, 10, "dairy"),
    "onion": CatalogItem("onion", "bag", 40, 4.0, 10, "produce"),
    "garlic": CatalogItem("garlic", "bulb", 15, 5.0, 14, "produce"),
    "butter": CatalogItem("butter", "pack", 60, 5.0, 20, "dairy"),
    "tea": CatalogItem("tea", "pack", 140, 10.0, None, "pantry"),
    "sugar": CatalogItem("sugar", "pack", 55, 10.0, None, "pantry"),
}

ALIASES = {
    "egg": "eggs",
    "loaf of bread": "bread",
    "milk carton": "milk",
    "spaghetti": "pasta",
    "penne": "pasta",
    "tomatoes": "tomato sauce",
    "tomato puree": "tomato sauce",
    "tomato pasta sauce": "tomato sauce",
    "cheddar": "cheese",
    "onions": "onion",
    "garlic cloves": "garlic",
}


def resolve_item(item: str) -> str:
    normalized = normalize_item(item)
    return ALIASES.get(normalized, normalized)


def get_catalog_item(item: str) -> CatalogItem:
    """Return a useful fallback for items the starter catalog does not know."""
    resolved = resolve_item(item)
    known = CATALOG.get(resolved)
    if known is not None:
        return known
    return replace(CatalogItem(item="unknown"), item=resolved)
