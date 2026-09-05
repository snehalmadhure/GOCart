from pantry_restock_agent.shopping import filter_against_pantry, generate_shopping_list


def test_intent_parser_builds_recipe_list() -> None:
    shopping_list = generate_shopping_list("Pasta dinner for 4 people")

    assert shopping_list["matched_recipe"] == "pasta"
    assert shopping_list["servings"] == 4
    assert next(item for item in shopping_list["items"] if item["item"] == "pasta")["quantity"] == 2


def test_pantry_filter_flags_duplicate_purchase() -> None:
    shopping_list = generate_shopping_list("Pasta dinner for 2")
    pantry = [{"item": "pasta", "estimated_quantity_left": 2, "status": "ok"}]

    filtered = filter_against_pantry(shopping_list, pantry)

    assert any(item["item"] == "pasta" for item in filtered["already_have"])
    assert not any(item["item"] == "pasta" for item in filtered["needs_to_buy"])
