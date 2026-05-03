# Traffic Management — Group 3

We started from GP2’s Postgres layer and added MongoDB and Redis for GP3, with a small Python CLI on top. Docker Compose runs Postgres, Mongo, Redis, and the app together.

## Prerequisites

- Python 3.10+  
- For running Postgres on your laptop (not in Docker): PostgreSQL 14+ and a user that can load `postgresql/schema.sql` and `data.sql`.

MongoDB and Redis don’t need to be installed locally if you only use Docker—the images in compose are enough.  

Handy tools: **mongosh** (run the `.js` files under `mongodb/`), **redis-cli** (poke Redis on `localhost` when ports are exposed).

Docker Desktop / Docker Engine + Compose v2 if you use the stack below.

## Docker quick start

From the repo root:

```bash
cp .env.example .env    # tweak ports / DB names if you changed them
docker compose up --build
```

That brings up postgres, mongodb, redis, mongo-seed (runs `mongodb/mongo_setup.js` then `mongo_data.js`), then the **app** container after seed finishes. Postgres applies `schema.sql` before `data.sql` (see `docker-compose.yml`).

Blow away volumes when you change SQL or Mongo seed scripts and need a clean load:

```bash
docker compose down -v
docker compose up --build
```

Containers talk to each other by service name (`postgres`, `mongodb`, `redis`). From your host, use **localhost** and the published ports (defaults 5432 / 27017 / 6379 unless you remapped them in `.env`).

For Mongo shell scripts, use `mongosh … --file`. Don’t pipe big files into mongosh stdin—it flakes.

## Architecture: what lives where

Rough sketch from our polyglot design doc:


| Data                                           | PostgreSQL | MongoDB | Redis |
| ---------------------------------------------- | ---------- | ------- | ----- |
| Intersection / road / zone / facility metadata | ✓          |         |       |
| Sensor + traffic signal configuration          | ✓          |         |       |
| Maintenance schedules + crews                  | ✓          |         |       |
| Emergency routes + usage                       | ✓          |         |       |
| Weather station metadata                       | ✓          |         |       |
| Traffic flow events, sensor readings           |            | ✓       |       |
| Incident reports (nested docs)                 |            | ✓       |       |
| Weather readings (Mongo collection)            |            | ✓       |       |
| Live signal state, per-intersection metrics    |            |         | ✓     |
| Congestion rankings, recent-incidents queue    |            |         | ✓     |
| Traffic alerts (pub/sub)                       |            |         | ✓     |


Postgres = structured stuff we join on. Mongo = noisy telemetry and incident detail. Redis = fast lookups and messaging—not where we store the canonical history.

## Repository layout


| Path                                                                | Purpose                                    |
| ------------------------------------------------------------------- | ------------------------------------------ |
| `postgresql/schema.sql`, `data.sql`                                 | DDL + seed                                 |
| `postgresql/queries.sql`                                            | Extra SQL—run with `psql` when you want it |
| `mongodb/mongo_setup.js`, `mongo_data.js`, `mongo_queries.js`       | Mongo setup, data, queries                 |
| `config/`, `models/`, `repositories/postgres/`, `services/`, `cli/` | Python code                                |
| `docker-compose.yml`, `Dockerfile`                                  | Stack definition                           |
| `.env.example`                                                      | Copy to `.env`                             |


Everything lives at the repo root—no `src/` folder.

## Environment

Copy `.env.example` → `.env`.

Local runs use `DB_`* for Postgres (see `config/database.py`). If `DB_USER` is blank we fall back to your OS username (`whoami`).

Compose fills in `PG_*`, `MONGO_DB`, ports, etc. where `docker-compose.yml` references them. Mongo/Redis in this compose file aren’t password-protected on the internal network.

Commit `.env` or don’t—follow whatever the assignment says this semester.

## Python

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Unified CLI operations

Cross-database menu entries we’re adding for GP3 (minimum two):

1. **Intersection dashboard** — Postgres row for the intersection, recent Mongo traffic/sensor docs, Redis for live metrics / signal snapshot.
2. **Report new incident** — Postgres for whatever stays relational, Mongo for the full incident payload, Redis for pub/sub + queuing recent incidents.

Nice-to-have third: **top congested intersections** — Redis sorted set + Postgres names.

GP2 menu options stay; add the new entries in `cli/main.py`.

## Run the CLI

Load postgres locally if you’re not using Docker, then:

```bash
python3 -m cli.main
```

With compose, use the **app** service—`docker-compose.yml` already points it at `postgres`, `mongodb`, and `redis`.

## Tests

Postgres needs schema + data loaded and `.env` pointing at it:

```bash
python3 -m pytest tests/ -v
```

