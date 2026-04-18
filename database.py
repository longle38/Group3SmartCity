import os
from pathlib import Path

import psycopg
import psycopg_pool
from dotenv import load_dotenv
from psycopg_pool import PoolTimeout

# Project root = parent of `src/` (this file lives in src/config/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


class DatabaseConfig:
    _pool = None

    @classmethod
    def _conninfo(cls):
        """Build a libpq connection string from environment variables."""
        # Homebrew Postgres on macOS: superuser is usually $USER, not `postgres`.
        db_user = os.getenv("DB_USER") or os.getenv("USER", "postgres")
        return (
            f"host={os.getenv('DB_HOST', 'localhost')} "
            f"port={os.getenv('DB_PORT', '5432')} "
            f"dbname={os.getenv('DB_NAME', 'traffic_management')} "
            f"user={db_user} "
            f"password={os.getenv('DB_PASSWORD', '')} "
            f"connect_timeout={os.getenv('DB_CONNECT_TIMEOUT', '10')} "
            # Avoid macOS libpq GSSAPI/Kerberos noise on TCP (harmless elsewhere).
            f"gssencmode={os.getenv('PG_GSSENCMODE', 'disable')}"
        )

    @classmethod
    def initialize(cls):
        """Create the connection pool. Call once at application startup."""
        try:
            cls._pool = psycopg_pool.ConnectionPool(
                conninfo=cls._conninfo(),
                min_size=2,
                max_size=10,
                timeout=float(os.getenv("DB_POOL_TIMEOUT", "60")),
                open=True,
            )
            # Prove we can talk to Postgres (pool may report "open" before checkout works).
            with cls._pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            print("Database connection pool initialized successfully.")
        except (psycopg.OperationalError, PoolTimeout) as e:
            print("Error: Cannot connect to database. Check .env and that Postgres is running.")
            print(f"Details: {e}")
            raise SystemExit(1)

    @classmethod
    def get_connection(cls):
        """
        Borrow a connection from the pool.

        Usage:
            with DatabaseConfig.get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute("SELECT ...")

        The connection is automatically returned to the pool
        when the with-block exits, even if an exception occurs.
        psycopg3 auto-commits on clean exit and auto-rolls back
        on exception. For explicit transaction control, use
        conn.transaction().
        """
        if cls._pool is None:
            cls.initialize()
        return cls._pool.connection()

    @classmethod
    def close_all(cls):
        """Close all connections. Call at application shutdown."""
        if cls._pool is not None:
            cls._pool.close()
            cls._pool = None
            print("Database connection pool closed.")
