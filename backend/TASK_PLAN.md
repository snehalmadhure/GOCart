# Backend task plan

Work in a feature branch, for example `backend/pantry-api`. Keep every task
small enough to commit and test independently.

## Phase 0 — Align with the team (30–45 minutes)

- [ ] Share the API payloads in `backend/README.md` with the frontend and ML
  teammates.
- [ ] Confirm the exact item fields: `item_name`, `quantity`, `unit`,
  `purchased_at`, and optional `expires_at`.
- [ ] Agree that dates are UTC ISO 8601 strings and quantities are decimal.
- [ ] Ask ML for the initial input/output contract of
  `estimate_consumption(...)` and `generate_list(...)`.
- [ ] Put any finalized cross-team contracts in the root `README.md`.

**Done when:** all teammates can build against the same mock JSON without
waiting for another layer.

## Phase 1 — Bootstrap the API (half day)

- [ ] Create `backend/requirements.txt` with FastAPI, Uvicorn, SQLAlchemy,
  Pydantic, and pytest.
- [ ] Create `app/main.py` and expose `GET /health`.
- [ ] Create `app/database.py` with a local SQLite database URL from an
  environment variable, defaulting to `sqlite:///./gocart.db`.
- [ ] Add application startup code that creates tables in development.
- [ ] Start the server with `uvicorn app.main:app --reload` and confirm
  `/docs` opens.
- [ ] Add a health-endpoint test.

**Commit:** `feat(backend): bootstrap FastAPI service`

## Phase 2 — Purchase logging and storage (1 day)

- [ ] Add `Item` and `Purchase` SQLAlchemy models.
- [ ] Add Pydantic request and response schemas.
- [ ] Create `POST /api/v1/purchases`.
- [ ] On a new item name, create an `Item`; otherwise reuse it
  case-insensitively.
- [ ] Create `GET /api/v1/purchases` with pagination and optional item filter.
- [ ] Validate positive quantity, supported unit, valid date ordering, and no
  blank item names.
- [ ] Write API tests for success and invalid payloads.

**Commit:** `feat(backend): add purchase logging API`

## Phase 3 — Virtual pantry state (1–1.5 days)

- [ ] Add `PantryState` model with quantity remaining, days left, run-out date,
  status, and calculation time.
- [ ] Create a temporary prediction adapter returning predictable test values.
- [ ] Write `refresh_pantry_item(item_id)` service.
- [ ] Call refresh after every successful purchase creation.
- [ ] Create `GET /api/v1/pantry` and support filtering by status.
- [ ] Return `unknown` when purchase history is insufficient.
- [ ] Add tests for `in_stock`, `low`, `out`, `expired`, and `unknown`.

**Commit:** `feat(backend): expose virtual pantry state`

## Phase 4 — ML integration boundary (half day)

- [ ] Define typed `ConsumptionEstimate` and `SuggestedItem` models.
- [ ] Make `services/prediction.py` the only backend module that imports from
  `ml/`.
- [ ] Replace the temporary adapter with ML's agreed function when ready.
- [ ] Handle ML failures safely: retain last pantry state and return a useful
  API error/log entry rather than corrupting data.
- [ ] Add one integration test with a fake ML implementation.

**Commit:** `feat(backend): integrate consumption prediction adapter`

## Phase 5 — Restock reminder batching (1 day)

- [ ] Add `ReminderBatch` and `ReminderBatchItem` models.
- [ ] Implement `build_or_update_reminder_batch()`.
- [ ] Include urgent items (run out in 3 days); add optional near-future items
  only where appropriate for the delivery threshold.
- [ ] Prevent duplicated items in open batches.
- [ ] Create `GET /api/v1/restock-alerts`.
- [ ] Create an endpoint to dismiss or mark a batch as seen.
- [ ] Add tests for grouping, deduplication, and repeated refreshes.

**Commit:** `feat(backend): add batched restock alerts`

## Phase 6 — Generated-list bridge (half–1 day)

- [ ] Create `POST /api/v1/shopping-lists/generate`.
- [ ] Send the intent and current pantry state to the ML list function.
- [ ] Flag suggestions already sufficiently available in the pantry.
- [ ] Return editable suggestions; do not place an order or modify purchases.
- [ ] Add duplicate-nudge and empty-intent tests.

**Commit:** `feat(backend): add pantry-aware shopping lists`

## Phase 7 — Frontend handoff and quality pass (half day)

- [ ] Add CORS for the frontend's development origin only.
- [ ] Provide a `.env.example` without secrets.
- [ ] Ensure every endpoint has clear FastAPI `/docs` descriptions and examples.
- [ ] Run all tests and manually test the core flow in `/docs`.
- [ ] Give frontend a URL, mock data option, and a list of final endpoints.
- [ ] Open a pull request with setup instructions and test results.

**Done when:** a frontend user can log milk, see its pantry status, receive a
batched restock alert, and generate a pantry-filtered shopping list.

## Recommended execution order

```text
Bootstrap → purchases → pantry with mock ML → alerts → list bridge → real ML → frontend integration
```

Do not wait for the ML model before completing Phases 1–3: use the temporary
adapter so the API and UI can already be integrated and tested.
