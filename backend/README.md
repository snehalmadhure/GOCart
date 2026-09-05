# GOCart backend plan

The backend is responsible for storing purchases, exposing the virtual pantry,
and turning predictions into useful restock reminders. Build it as a FastAPI
application backed by SQLite for the first single-user version.

## Scope and ownership

- Record purchases: item, quantity, unit, purchase date, and optional expiry
  date.
- Maintain a queryable pantry state: estimated quantity remaining, predicted
  run-out date, and low-stock status.
- Provide stable HTTP endpoints for the React frontend.
- Call ML functions through a small adapter, so the backend does not depend on
  a particular forecasting implementation.
- Group low-stock items into a single reminder rather than emitting one alert
  per item.

Out of scope for this first pass: authentication, shared households, real-time
sync, push-notification delivery, order-history scraping, and automatic cart
checkout.

## Suggested structure

```text
backend/
├── app/
│   ├── main.py             # FastAPI app and router registration
│   ├── database.py         # SQLite engine, session, initialization
│   ├── models.py           # SQLAlchemy tables
│   ├── schemas.py          # Pydantic request/response models
│   ├── routers/
│   │   ├── purchases.py
│   │   ├── pantry.py
│   │   ├── alerts.py
│   │   └── lists.py
│   └── services/
│       ├── pantry.py       # state calculation and refresh
│       ├── prediction.py   # adapter around ml/ functions
│       └── reminders.py    # batching rules
├── tests/
├── requirements.txt
└── README.md
```

## Data model

Start with these tables. Keep `user_id` nullable/defaulted for now so the
single-user app can add authentication later without a destructive migration.

| Table | Important fields | Purpose |
| --- | --- | --- |
| `items` | `id`, `name`, `category`, `default_unit`, `low_stock_days` | Canonical item names and display/default settings. |
| `purchases` | `id`, `item_id`, `quantity`, `unit`, `purchased_at`, `expires_at`, `created_at` | Immutable purchase history; never overwrite past orders. |
| `pantry_states` | `item_id`, `estimated_quantity`, `unit`, `estimated_days_left`, `predicted_run_out_at`, `last_calculated_at`, `status` | Cached, frontend-friendly current state. Recalculate after a purchase or prediction refresh. |
| `reminder_batches` | `id`, `status`, `scheduled_for`, `created_at`, `sent_at`, `estimated_cart_total` | One grouped notification/event. |
| `reminder_batch_items` | `batch_id`, `item_id`, `suggested_quantity`, `reason` | Items included in a reminder batch. |

Use ISO 8601 UTC timestamps in the API and database. Store quantities as
decimal values, not floats. A purchase should contain a unit (`count`, `g`,
`ml`, `pack`, etc.); only calculate arithmetic when comparable units match.

## Fixed API contracts

Agree on these contracts with the frontend and ML teammates before coding.

### Create a purchase

`POST /api/v1/purchases`

```json
{
  "item_name": "milk",
  "quantity": 1,
  "unit": "litre",
  "purchased_at": "2026-09-05T00:00:00Z",
  "expires_at": "2026-09-08T00:00:00Z"
}
```

Return `201` with the stored purchase and trigger a pantry refresh for that
item.

### Fetch the pantry

`GET /api/v1/pantry?status=all`

```json
{
  "items": [
    {
      "item_id": 1,
      "item_name": "milk",
      "estimated_quantity": 0.35,
      "unit": "litre",
      "days_left": 1.5,
      "run_out_at": "2026-09-06T12:00:00Z",
      "status": "low",
      "last_calculated_at": "2026-09-05T08:00:00Z"
    }
  ]
}
```

Statuses: `in_stock`, `low`, `out`, `expired`, and `unknown`. `unknown` is
important: one recorded purchase is not enough to make a trustworthy rate
prediction.

### Fetch restock alerts

`GET /api/v1/restock-alerts?include_dismissed=false`

Return pending reminder batches and their included items. The frontend uses
this for the reminder UI, rather than calculating reminders itself.

### Shopping-list integration

`POST /api/v1/shopping-lists/generate`

The backend forwards `intent` to the ML list generator, then checks returned
items against `pantry_states`. Return each suggestion with a `pantry_warning`
when it is already sufficiently stocked. The first implementation may use a
deterministic mock adapter until ML is ready.

## ML adapter boundary

Do not let route handlers import notebooks or model internals. Define a small
interface in `services/prediction.py`:

```python
estimate_consumption(item, purchases, as_of) -> ConsumptionEstimate
generate_list(intent, pantry_items) -> list[SuggestedItem]
```

`ConsumptionEstimate` should expose `daily_usage`, `estimated_quantity`,
`days_left`, `run_out_at`, and `confidence`. The backend maps this into
`pantry_states`; the ML teammate can replace the implementation without
changing API responses.

## Reminder batching policy, version 1

Run it after each pantry refresh and once daily.

1. Select items with `status in (low, out, expired)` or `days_left <= 2`.
2. Do not create a second open batch if one already contains the same item.
3. Create or update one pending batch for items expected to run out within the
   next 3 days.
4. Include optional items that run out within 7 days only when doing so helps
   meet the configurable delivery threshold.
5. Schedule the batch for the earliest run-out time, capped to a user-friendly
   daytime window. The backend creates the batch; notification delivery can be
   wired in later.

Keep threshold and time-window settings in configuration, not hard-coded in
the algorithm.

## Implementation milestones

1. **Bootstrap:** create FastAPI app, dependency file, health endpoint,
   SQLite connection, and database initialization.
2. **Persistence:** implement `items` and `purchases` models plus create/list
   purchase endpoints. Validate positive quantities, known units, and dates.
3. **Pantry:** add the prediction adapter and `pantry_states`; refresh only the
   affected item after a purchase. Use a simple average/mock prediction first.
4. **Alerts:** implement reminder-batch tables, batch policy, and read/dismiss
   alert endpoints.
5. **Lists:** add the generated-list endpoint and pantry duplicate warnings.
6. **Integration:** replace mock adapter with ML functions, enable CORS for the
   React development origin, and have the frontend run against the live API.

## Test plan

- Unit tests for model validation and quantity/unit handling.
- Service tests covering: new purchase refreshes pantry; expired item wins over
  normal low-stock status; insufficient history returns `unknown`.
- Reminder tests covering deduplication, 3-day grouping, and no duplicate open
  batch after repeated refreshes.
- API tests for validation errors, pagination/filtering, and response contract
  snapshots.
- A short manual smoke test in FastAPI `/docs`: create milk purchase, retrieve
  pantry, force a low prediction, then retrieve the resulting batch.

## First task checklist

- [ ] Create a `backend` branch.
- [ ] Bootstrap FastAPI and SQLite.
- [ ] Commit the `items` and `purchases` schema with tests.
- [ ] Share the API examples above with teammates and lock the field names.
- [ ] Add pantry state after the ML adapter contract is approved.

## Run locally

From the `backend/` directory on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation. Copy
`.env.example` to `.env` only if your shell or deployment process loads env
files; otherwise set its values in your terminal or service configuration.

Run the backend test suite with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Implemented endpoints

| Method | Route | Use |
| --- | --- | --- |
| `GET` | `/health` | API health check. |
| `POST` | `/api/v1/purchases` | Log a purchase and refresh its pantry state. |
| `GET` | `/api/v1/purchases` | List purchases; accepts `item_name`, `offset`, and `limit`. |
| `GET` | `/api/v1/pantry` | Fetch pantry state; accepts `status`. |
| `GET` | `/api/v1/restock-alerts` | Fetch active reminder batches. |
| `POST` | `/api/v1/restock-alerts/{batch_id}/dismiss` | Dismiss a reminder batch. |
| `POST` | `/api/v1/shopping-lists/generate` | Generate a pantry-filtered shopping list from `intent`. |

The current `services/prediction.py` is a deterministic placeholder. Phase 4
is complete from the backend perspective: when the ML teammate is ready,
replace only `estimate_consumption` and `generate_list` there while retaining
their typed return contracts. The HTTP API and database code do not need to
change.
