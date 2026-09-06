# Pantry Restock Agent

A responsive React frontend for a single-user, AI-assisted pantry planning experience. It shows estimated pantry inventory, helps log purchases, groups restock reminders, and creates editable shopping plans without attempting checkout or ordering.

## Stack

- React + Vite
- React Router
- Tailwind CSS
- Native `fetch` service layer (with independent mock-data mode)
- Lucide icons

## Run locally

```bash
npm install
npm run dev
```

Copy `.env.example` to `.env` if you need to override defaults. The application is fully usable by default with realistic in-memory demo data.

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK_API=true
```

Set `VITE_USE_MOCK_API=false` to call the backend specified by `VITE_API_BASE_URL`. Errors are shown in the UI with retry actions.

## Routes

- `/pantry` — virtual pantry, filters, estimates, and detail dialog
- `/purchases` — purchase search/history, add/edit/delete, and import-ready flow
- `/reminders` — intelligently batched restock reminders with snooze/dismiss actions
- `/shopping-list` — natural-language generation, pantry duplicate nudges, editable list and confirmation

`/` redirects to `/pantry`.

## Backend integration

Endpoint access is centralized under `src/services/`. When mock mode is disabled, the app expects:

```text
GET    /api/pantry
GET    /api/pantry/:id
GET    /api/purchases
POST   /api/purchases
PUT    /api/purchases/:id
DELETE /api/purchases/:id
POST   /api/purchases/import
GET    /api/reminders
POST   /api/reminders/:id/snooze
POST   /api/reminders/:id/dismiss
POST   /api/shopping-list/generate
POST   /api/shopping-list/:id/confirm
```

The API contracts tolerate extra backend fields; page-specific mock data in `src/data/mockData.js` demonstrates the expected core shapes.

## Full-stack development

The repository now has three connected layers:

```text
React frontend (src/) → FastAPI backend (backend/) → Pantry ML package (ai-ml/)
```

The backend imports the repository-local `ai-ml/pantry_restock_agent` package
through `backend/app/services/prediction.py`. Purchase logging refreshes pantry
state with the ML forecast; generated shopping lists use the ML pantry-aware
list generator.

Start the backend in one terminal:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

In a second terminal, set `VITE_USE_MOCK_API=false` in a root `.env` file and
start the frontend:

```powershell
npm run dev
```

The frontend sends all live requests to `/api/v1/*` and maps responses to its
display models in `src/services/backendMappers.js`. Keep mock mode enabled when
you only want a frontend design demo without the backend running.

### Verification

Run each Python project from its own directory/environment:

```powershell
# backend
cd backend
.\.venv\Scripts\python.exe -m pytest -q

# ML package
cd ..\ai-ml
python -m pytest -q

# frontend (from repository root)
npm run build
```

## Structure

```text
src/
  components/     shared layout, modal, states, notifications
  data/           realistic mock API data
  hooks/          async server-state helper
  pages/          route-level UI
  services/       centralized backend and mock API layer
  utils/          formatting and pantry status rules
```
