# Traffic Management (GP2)

PostgreSQL-backed traffic management data layer with a menu-driven Python CLI (psycopg3, repository and service layers).

## Prerequisites

- **Python** 3.10 or newer
- **PostgreSQL** 14 or newer (server running and reachable from your machine)
- A database user that can create objects and insert data (for local development, the default `postgres` superuser is common)

## Repository layout


| Path                     | Purpose                                                                   |
| ------------------------ | ------------------------------------------------------------------------- |
| `postgresql/schema.sql`  | DDL: tables, constraints, indexes, triggers (create when available)       |
| `postgresql/data.sql`    | Sample `INSERT` data (create when available)                              |
| `postgresql/queries.sql` | Six or more documented analytical queries (GP2 Part 2)                    |
| `src/`                   | Appplication code (`config`, `models`, `repositories`, `services`, `cli`) |
| `src/tests/`             | Optional `pytest` tests (require a loaded database)                       |
| `.env.example`           | Template for database connection variables                                |
| `requirements.txt`       | Python dependencies                                                       |


## Database setup

1. **Create an empty database** (name can match `DB_NAME` in `.env`; default is `traffic_management`):
  ```bash
   createdb traffic_management
  ```
   Or from `psql` as a superuser:
2. **Load schema and data** once `postgresql/schema.sql` and `postgresql/data.sql` exist in this repo:
  ```bash
   psql -U postgres -d traffic_management -f postgresql/schema.sql
   psql -U postgres -d traffic_management -f postgresql/data.sql
  ```
   Adjust `-U` and connection options if your PostgreSQL user or host differs.
3. **Optional**: run Part 2 queries for grading or ad hoc checks:
  ```bash
   psql -U postgres -d traffic_management -f postgresql/queries.sql
  ```

## Environment configuration

1. Copy the example env file and edit values for your machine:
  ```bash
   cp .env.example .env
  ```
2. Set at least `DB_PASSWORD` if your PostgreSQL user requires a password. The application reads:
  - `DB_HOST` (default `localhost`)
  - `DB_PORT` (default `5432`)
  - `DB_NAME` (default `traffic_management`)
  - `DB_USER` (default `postgres`)
  - `DB_PASSWORD` (default empty string)
3. **Do not commit `.env`**; it should stay local and out of version control. Only `.env.example` belongs in the repo.

## Python setup

From the **project root** (the directory that contains `src/` and `requirements.txt`):

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the CLI

From the project root, with the virtual environment activated:

```bash
PYTHONPATH=src python3 -m cli.main
```

Alternatively, running the entry script directly also adds `src` to the module path:

```bash
python3 src/cli/main.py
```

The menu supports intersection lookup, high-incident reporting, system metrics, and incident counts by severity. A working database that matches the application schema is required.

## Tests (optional)

Tests under `src/tests/` expect PostgreSQL to be running and the same `.env` (or defaults) to point at a database where the schema is loaded.

Install test tooling if needed:

```bash
pip install pytest pytest-cov
```

Run tests from the project root:

```bash
PYTHONPATH=src pytest src/tests/ -v
```

With coverage:

```bash
PYTHONPATH=src pytest src/tests/ --cov=src --cov-report=html
```

