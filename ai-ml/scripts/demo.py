"""Run an end-to-end pantry-agent example."""

from __future__ import annotations

import json
from datetime import date

from pantry_restock_agent.api import run_agent
from pantry_restock_agent.synthetic import generate_synthetic_history


def main() -> None:
    dataset = generate_synthetic_history(total_days=180, start_date=date(2026, 1, 1), seed=7)
    result = run_agent(
        dataset.events,
        today=date(2026, 6, 29),
        intent="Pasta dinner for 4 people",
        delivery_threshold=199,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
