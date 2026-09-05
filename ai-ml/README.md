# Pantry Restock Agent

An ML-first pantry assistant that learns how quickly a person uses groceries, estimates what remains, predicts run-out dates, and turns those predictions into useful restock decisions.

This version is deliberately built as a strong project foundation instead of a collection of disconnected scripts. It has a fixed data contract, deterministic synthetic data with known ground truth, confidence-aware forecasting, an event-based virtual pantry, shopping-list reasoning, and tests.

## What it does

- Learns `days_per_unit` from purchase history using a robust, recency-weighted estimator.
- Handles bulk purchases by dividing the next purchase gap by the prior quantity.
- Builds a virtual pantry by replaying purchase events and estimated daily consumption.
- Produces a run-out date, low-stock state, and confidence score for every item.
- Generates a recipe shopping list from a short natural-language intent.
- Removes or flags list items that are already estimated to be in the pantry.
- Batches low and soon-to-be-low items toward a delivery threshold.
- Evaluates the estimator against synthetic ground truth, so you can quantify model quality.

## Project layout

```text
pantry_restock_agent/
├── pantry_restock_agent/   # Importable ML and agent package
├── scripts/                # Demo and synthetic evaluation entry points
├── tests/                  # Focused unit tests
├── data/                   # Example backend-compatible purchase data
├── README.md
└── pyproject.toml
```

## Quick start (Windows)

Install Python 3.10 or newer first. During installation, select **Add Python to PATH**.

```powershell
cd C:\Users\parid\Documents\Codex\2026-09-05\h\outputs\pantry_restock_agent
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m scripts.demo
python -m scripts.evaluate
python -m pytest
```

The runtime package itself only uses Python's standard library. `pytest` is only needed for the test suite.

## Backend contract

Every purchase sent to the ML layer follows this shape:

```json
{
  "item": "milk",
  "quantity": 1,
  "date": "2026-06-01",
  "unit": "carton",
  "unit_price": 68,
  "expires_in_days": 5
}
```

Only `item`, `quantity`, and `date` are required. The rest makes recommendations and expiry hints more useful.

The simplest backend integration is one function call:

```python
from pantry_restock_agent.api import run_agent

result = run_agent(
    purchases=purchase_rows_from_database,
    intent="Pasta dinner for 4",
    delivery_threshold=199,
)
```

`result` is a JSON-ready dictionary containing `forecasts`, `pantry`, `restock_plan`, and (when an intent is supplied) a pantry-aware `shopping_list`.

## Why this is a credible ML baseline

The core estimator is not pretending to know inventory perfectly. It makes its assumptions visible:

1. A purchase quantity represents comparable units for that item, such as cartons of milk or loaves of bread.
2. The gap after a two-pack purchase represents roughly two units of usage, so the gap is divided by the prior quantity.
3. Extreme gaps are clipped with a median/MAD-based robust rule before fitting.
4. Newer observations carry more weight than older behavior.
5. Confidence increases with observations and decreases with irregular purchase cadence.

That gives you a useful, explainable v1. Later experiments can compare it with a Bayesian state-space model, survival model, or sequence model without changing the backend contract.

## Main functions

```python
from pantry_restock_agent.forecasting import fit_consumption_model, forecast_restocks
from pantry_restock_agent.pantry import build_virtual_pantry
from pantry_restock_agent.shopping import generate_pantry_aware_shopping_list
from pantry_restock_agent.reminders import plan_restock_bundle
```

See [scripts/demo.py](scripts/demo.py) for an end-to-end example and [scripts/evaluate.py](scripts/evaluate.py) for a reproducible evaluation against synthetic truth.

## A sensible next iteration

Keep this estimator as the benchmark. Once you have real purchase logs, measure per-item MAE for `days_per_unit`, calibrate the confidence score, and add an explicit correction action in the UI such as “I still have half a carton.” Those corrections become useful labels for a more advanced inventory model.
