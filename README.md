# Traffic Management — Group 3

Polyglot traffic data layer: **PostgreSQL** (GP2), plus **MongoDB** and **Redis** for GP3, with a small Python CLI on top of `psycopg3`, repository classes, and optional Docker Compose.

## Prerequisites

- **Python** 3.10+ recommended  
- **PostgreSQL** 14+ if you run SQL locally  
- **Docker** + Docker Compose

## Layout


| Path                                                                | Purpose                                                         |
| ------------------------------------------------------------------- | --------------------------------------------------------------- |
| `postgresql/schema.sql`, `data.sql`                                 | DDL and seed data                                               |
| `postgresql/queries.sql`                                            | Extra analytical SQL (run manually when you want those reports) |
| `mongodb/mongo_setup.js`, `mongo_data.js`, `mongo_queries.js`       | Mongo collections, seed data, assignment queries                |
| `config/`, `models/`, `repositories/postgres/`, `services/`, `cli/` | Application code                                                |
| `tests/`                                                            | `pytest` against Postgres (needs DB + schema loaded)            |
| `docker-compose.yml`, `Dockerfile`                                  | Three databases + app container                                 |
| `.env.example`                                                      | Copy to `.env` and adjust                                       |


Application packages live at the **repo root** (there is no `src/` folder).

## Environment

Copy `cp .env.example .env` and edit.

**Local CLI** uses `DB_`* (see `config/database.py`): host, port, database name, user, password, optional timeouts. Empty `DB_USER` falls back to your OS user, which matches typical Homebrew Postgres on macOS.

**Docker Compose** substitutes `PG_`*, `MONGO_DB`, and port overrides from `.env` where `docker-compose.yml` references them. The Mongo and Redis services in the starter run **without auth** on the internal network; the app talks to `postgres`, `mongodb`, and `redis` by **service name**, not `localhost`.

Follow your current assignment brief for whether `.env` must be committed for grading.

## Python

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the CLI (local Postgres)

Load schema and data into your database, then:

```bash
python3 -m cli.main
```

No `PYTHONPATH` - the repo root is on the path when you use `python3 -m cli.main`.

Menu options include intersection lookup, high-incident intersections (90 days), system metrics, and incident counts by severity.

## Docker (GP3)

From the project root:

```bash
docker compose up --build
```

Postgres init runs `schema.sql` then `data.sql` (order is fixed in compose). The `mongo-seed` service runs `mongodb/mongo_setup.js` and `mongodb/mongo_data.js` once Mongo is healthy. To reset all DB volumes after changing SQL or Mongo scripts:

```bash
docker compose down -v
```

Run Mongo shell scripts **with `--file`** (e.g. copy into the container or mount them); piping large files into `mongosh` stdin can misfire.

## Tests

Requires Postgres with schema/data loaded and `.env` pointing at it:

```bash
python3 -m pytest tests/ -v
```

## Mongo / Redis from the host

With compose running, databases are usually reachable on `localhost` via the published ports (`5432`, `27017`, `6379` unless overridden in `.env`).