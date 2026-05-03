# Traffic Management Group 3

PostgreSQL-backed traffic management data layer with a menu-driven Python CLI (psycopg3, repository and service layers).

## Prerequisites

- **Python** 3.9 or newer (3.10+ recommended)
- **PostgreSQL** 14 or newer (server running and reachable from your machine)
- A database role that can create objects and load data

## Repository layout


| Path                     | Purpose                                                                  |
| ------------------------ | ------------------------------------------------------------------------ |
| `postgresql/schema.sql`  | DDL: tables, constraints, enums                                          |
| `postgresql/data.sql`    | Sample `INSERT` data                                                     |
| `postgresql/queries.sql` | Documented analytical queries                                            |
| `src/`                   | Application code (`config`, `models`, `repositories`, `services`, `cli`) |
| `src/tests/`             | Optional `pytest` tests (require a loaded database)                      |
| `.env.example`           | Template for database connection variables                               |
| `requirements.txt`       | Python dependencies                                                      |


## Database setup

1. **Create an empty database** (name should match `DB_NAME` in `.env`; default is `traffic_management`):
  ```bash
   createdb traffic_management
  ```
   If `createdb` is not on your PATH, create it from `psql` as a role that can create databases.
2. **Load schema and data** from the **project root**:
  ```bash
   psql -h 127.0.0.1 -p 5432 -d traffic_management -f postgresql/schema.sql
   psql -h 127.0.0.1 -p 5432 -d traffic_management -f postgresql/data.sql
  ```
   Adjust `**-h**`, `**-p**`, and **role** to match your machine. On a Homebrew Mac you often omit `-U` (uses your OS user) or pass `**-U "$(whoami)"`**. Do **not** assume `-U postgres` unless that role exists.
3. **Optional:** run Part 2 queries:
  ```bash
   psql -h 127.0.0.1 -p 5432 -d traffic_management -f postgresql/queries.sql
  ```

## Environment configuration

1. Copy the example env file and edit if needed:
  ```bash
   cp .env.example .env
  ```
2. Variables the app reads (see `src/config/database.py`):

  | Variable             | Notes                                                                          |
  | -------------------- | ------------------------------------------------------------------------------ |
  | `DB_HOST`            | Default `localhost`. `**127.0.0.1**`                                           |
  | `DB_PORT`            | Default `5432`.                                                                |
  | `DB_NAME`            | Default `traffic_management`.                                                  |
  | `DB_USER`            | If unset or empty, the app uses `**$USER**`                                    |
  | `DB_PASSWORD`        | Often empty for local trust/peer auth; set if your server requires a password. |
  | `DB_CONNECT_TIMEOUT` | Optional; default `10` (seconds) in the connection string.                     |
  | `DB_POOL_TIMEOUT`    | Optional; default `60` (pool checkout timeout).                                |
  | `PG_GSSENCMODE`      | Optional; default `**disable**`.                                               |
  | `CLI_DEBUG`          | Set to `1` to print tracebacks for unexpected CLI errors.                      |

3. **Do not commit `.env`**; keep it local. Only `.env.example` belongs in the repo.

## Python setup

From the **project root** (directory that contains `src/` and `requirements.txt`):

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the CLI

From the project root, with dependencies installed:

```bash
PYTHONPATH=src python3 -m cli.main
```

Alternatively:

```bash
python3 src/cli/main.py
```

(`src/cli/main.py` prepends `src` to `sys.path` when run as a script.)

The menu supports intersection lookup, high-incident intersections (90-day window), system metrics, and incident counts by severity. You need a database loaded from `postgresql/schema.sql` and `postgresql/data.sql` (or equivalent).

## Tests (optional)

Tests under `src/tests/` expect PostgreSQL running and `.env` pointing at a database where the schema is loaded.

```bash
pip install pytest pytest-cov
PYTHONPATH=src pytest src/tests/ -v
```

With coverage:

```bash
PYTHONPATH=src pytest src/tests/ --cov=src --cov-report=html
```

