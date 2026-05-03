# Traffic Management — Group 3

GP2 Postgres core extended with MongoDB and Redis for GP3; Python CLI on top. Docker Compose runs Postgres, MongoDB, Redis, and the app container.

## Prerequisites

- Python 3.10+  
- PostgreSQL 14+ only when Postgres runs outside Compose; DB role must apply `postgresql/schema.sql` and `data.sql`.  
- MongoDB + Redis not needed on the host if everything runs in Compose.  
- Optional: **mongosh**, **redis-cli** (inspect Mongo / Redis on exposed ports).  
- **Docker** with **Compose** for `docker-compose.yml`.

## Docker quick start

From the repository root:

```bash
cp .env.example .env
docker compose up --build
```

Services: `postgres`, `mongodb`, `redis`, `mongo-seed` (runs `mongodb/mongo_setup.js` then `mongo_data.js`), then `app`. Postgres loads `schema.sql` before `data.sql` per volume mounts in `docker-compose.yml`.

Reset data volumes after changing SQL or Mongo seed files:

```bash
docker compose down -v
docker compose up --build
```

Service discovery inside the network uses `postgres`, `mongodb`, `redis`. From the host, use `localhost` and the mapped ports (default **5432** / **27017** / **6379** if unchanged in `.env`).

Run Mongo scripts with `mongosh --file`, not stdin redirection.

## Architecture: data placement

| Data | PostgreSQL | MongoDB | Redis |
|------|:----------:|:-------:|:-----:|
| Intersection / road / zone / facility metadata | ✓ | | |
| Sensor + traffic signal configuration | ✓ | | |
| Maintenance schedules + crews | ✓ | | |
| Emergency routes + usage | ✓ | | |
| Weather station metadata | ✓ | | |
| Traffic flow events, sensor readings | | ✓ | |
| Incident reports (nested documents) | | ✓ | |
| Weather readings (Mongo collection) | | ✓ | |
| Live signal state, per-intersection metrics | | | ✓ |
| Congestion rankings, recent-incidents queue | | | ✓ |
| Traffic alerts (pub/sub) | | | ✓ |

PostgreSQL: relational reference data. MongoDB: high-volume / flexible documents. Redis: low-latency state and messaging; not the primary durable store.

## Repository layout

| Path | Purpose |
|------|---------|
| `postgresql/schema.sql`, `data.sql` | DDL + seed |
| `postgresql/queries.sql` | Extra SQL (`psql` as needed) |
| `mongodb/mongo_setup.js`, `mongo_data.js`, `mongo_queries.js` | Mongo setup, seed, queries |
| `config/`, `models/`, `repositories/postgres/`, `services/`, `cli/` | Python application |
| `docker-compose.yml`, `Dockerfile` | Container stack |
| `.env.example` | Environment template |

Packages sit at the repository root (no `src/` directory).

## Environment

Copy `.env.example` to `.env`.

- Host CLI: `DB_*` for Postgres (`config/database.py`). Empty `DB_USER` defaults to the current OS username.  
- Compose pulls `PG_*`, `MONGO_DB`, and ports from `.env` where `docker-compose.yml` references them. Mongo and Redis have no password on the compose network.

## Python

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Unified CLI operations

Cross-database menu entries:

1. **Intersection dashboard** — Postgres intersection row, recent Mongo traffic/sensor data, Redis live metrics / signal snapshot.  
2. **Report new incident** — relational writes to Postgres, incident document in Mongo, Redis pub/sub and recent-incidents queue.

Optional third: **top congested intersections** — Redis ranking + Postgres intersection metadata.

Keep existing GP2 actions; add unified entries in `cli/main.py`.

## Run the CLI

Without Docker: load Postgres schema and seed data, then:

```bash
python3 -m cli.main
```

With Docker: attach to the `app` service; `docker-compose.yml` sets `DB_HOST`, `MONGO_HOST`, `REDIS_HOST` to the compose services.

## Tests

Requires Postgres with schema/data loaded and `.env` configured:

```bash
python3 -m pytest tests/ -v
```
