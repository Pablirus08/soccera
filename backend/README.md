# SoccerA — Backend

Live soccer analysis and prediction platform. Phase 0-1: ingestion + storage
foundation. Prediction models, the API, and the dashboard come later.

## Architecture

```
src/soccera/
├── ingestion/
│   ├── domain.py              # canonical, source-agnostic models
│   ├── base.py                 # DataSourceAdapter interface
│   ├── providers/api_football/ # API-Football client, adapter, mappers
│   ├── providers/costa_rica/   # placeholder for the CR League scraper
│   └── sync/                   # historical backfill + live polling jobs
├── storage/
│   ├── models/                 # SQLAlchemy ORM models
│   ├── repositories/           # data access layer
│   ├── migrations/             # Alembic
│   └── database.py
├── models/                     # (Phase 2) Poisson/Dixon-Coles, Elo
└── api/                        # (Phase 3) FastAPI
```

Nothing in `storage/` or `sync/` imports from `providers/api_football/`. They
depend only on `ingestion.domain` models and the `DataSourceAdapter`
interface — swapping or adding a data source means writing one new adapter
class in `providers/`, no changes anywhere else.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
# edit .env — fill in API_FOOTBALL_KEY
```

## Running Postgres + Redis

```powershell
docker compose up -d postgres redis
alembic upgrade head
```

## Running ingestion

```powershell
# One-off historical backfill (league ID + season year, from API-Football)
python scripts/run_backfill.py 39 2024 2024-08-01 2025-05-31

# Continuous live-score polling
python scripts/run_live_poll.py
```

Or run everything (including the ingestion service) via Docker:

```powershell
docker compose up -d
```

## Tests

```powershell
pytest tests/unit               # no external dependencies
pytest tests/integration        # needs Postgres reachable at TEST_DATABASE_URL
                                 # (defaults to localhost:5432/soccera_test)
```

## Database migrations

```powershell
alembic revision --autogenerate -m "description"
alembic upgrade head
```
