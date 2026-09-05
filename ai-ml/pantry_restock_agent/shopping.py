"""Rule-based intent parsing and pantry-aware shopping-list logic.

This is an intentionally replaceable baseline. A later LLM tool can produce
the same list contract without changing the rest of the application.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from math import ceil
import re
from typing import Any

from .catalog import get_catalog_item, resolve_item


@dataclass(frozen=True)
class Ingredient:
    item: str
    quantity_per_serving: float
    minimum_quantity: int = 1


@dataclass(frozen=True)
class Recipe:
    name: str
    aliases: tuple[str, ...]
    ingredients: tuple[Ingredient, ...]


RECIPES = (
    Recipe(
        "pasta",
        ("pasta", "spaghetti", "penne"),
        (
            Ingredient("pasta", 0.5),
            Ingredient("tomato sauce", 0.25),
            Ingredient("cheese", 0.25),
            Ingredient("onion", 0.25),
            Ingredient("garlic", 0.25),
        ),
    ),
    Recipe(
        "sandwiches",
        ("sandwich", "sandwiches"),
        (
            Ingredient("bread", 0.25),
            Ingredient("cheese", 0.25),
            Ingredient("butter", 0.15),
            Ingredient("onion", 0.25),
        ),
    ),
    Recipe(
        "breakfast",
        ("breakfast", "brunch"),
        (
            Ingredient("eggs", 0.4),
            Ingredient("bread", 0.25),
            Ingredient("milk", 0.25),
            Ingredient("butter", 0.15),
        ),
    ),
    Recipe(
        "chai",
        ("chai", "tea"),
        (
            Ingredient("milk", 0.25),
            Ingredient("tea", 0.1),
            Ingredient("sugar", 0.1),
        ),
    ),
)


def _servings_from_intent(intent: str, default: int = 2) -> int:
    patterns = (
        r"\bfor\s+(\d+)\b",
        r"\b(\d+)\s+(?:people|persons|guests)\b",
        r"\bserves?\s+(\d+)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, intent.lower())
        if match:
            return max(1, int(match.group(1)))
    return default


def _recipe_from_intent(intent: str) -> Recipe | None:
    text = intent.lower()
    for recipe in RECIPES:
        if any(alias in text for alias in recipe.aliases):
            return recipe
    return None


def generate_shopping_list(intent: str) -> dict[str, Any]:
    """Turn a compact dinner/occasion intent into an editable shopping list."""
    if not intent or not intent.strip():
        raise ValueError("intent cannot be empty")

    recipe = _recipe_from_intent(intent)
    servings = _servings_from_intent(intent)
    if recipe is None:
        return {
            "intent": intent,
            "servings": servings,
            "matched_recipe": None,
            "items": [],
            "notes": ["No recipe template matched. Ask the user to add items manually."],
        }

    items = []
    for ingredient in recipe.ingredients:
        quantity = max(ingredient.minimum_quantity, ceil(ingredient.quantity_per_serving * servings))
        catalog_item = get_catalog_item(ingredient.item)
        items.append(
            {
                "item": ingredient.item,
                "quantity": quantity,
                "unit": catalog_item.unit,
                "estimated_unit_price": catalog_item.typical_price,
            }
        )

    return {
        "intent": intent,
        "servings": servings,
        "matched_recipe": recipe.name,
        "items": items,
        "notes": ["Quantities are starter estimates and should remain editable in the UI."],
    }


def filter_against_pantry(
    shopping_list: Mapping[str, Any],
    pantry: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Separate required purchases from items already likely to be on hand."""
    pantry_by_item = {resolve_item(str(row["item"])): row for row in pantry}
    needs_to_buy: list[dict[str, Any]] = []
    already_have: list[dict[str, Any]] = []

    for requested in shopping_list.get("items", []):
        item = resolve_item(str(requested["item"]))
        pantry_item = pantry_by_item.get(item)
        available = float(pantry_item.get("estimated_quantity_left", 0)) if pantry_item else 0.0
        requested_quantity = float(requested["quantity"])
        if pantry_item and pantry_item.get("status") == "ok" and available >= requested_quantity:
            already_have.append(
                {
                    **requested,
                    "available_quantity": round(available, 2),
                    "nudge": f"You likely already have enough {item}. Review before buying again.",
                }
            )
            continue

        missing_quantity = max(1, ceil(requested_quantity - available))
        needs_to_buy.append({**requested, "quantity": missing_quantity})

    return {
        "intent": shopping_list["intent"],
        "servings": shopping_list["servings"],
        "matched_recipe": shopping_list["matched_recipe"],
        "needs_to_buy": needs_to_buy,
        "already_have": already_have,
        "notes": list(shopping_list.get("notes", [])),
    }


def generate_pantry_aware_shopping_list(
    intent: str,
    pantry: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    return filter_against_pantry(generate_shopping_list(intent), pantry)
