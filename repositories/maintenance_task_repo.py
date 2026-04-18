import os
import psycopg
import psycopg_pool
from psycopg.rows import dict_row
from models.maintenance_task import MaintenanceTask
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    _pool: psycopg_pool.ConnectionPool | None = None

    @classmethod
    def _conninfo(cls) -> str:
        return (
            f"host={os.getenv('DB_HOST', 'localhost')} "
            f"port={os.getenv('DB_PORT', '5432')} "
            f"dbname={os.getenv('DB_NAME', 'traffic_management')} "
            f"user={os.getenv('DB_USER', 'postgres')} "
            f"password={os.getenv('DB_PASSWORD', '')}"
        )
    
    @classmethod
    def initialize(cls) -> None:
        try:
            cls._pool = psycopg_pool.ConnectionPool(conninfo=cls._conninfo(), min_size=2, max_size=10, open=True)
        except psycopg.OperationalError as e:
            print(f"Error: Cannot connect to the database. Check .env settings.")
            print(f"Details: {e}")
            raise SystemExit(1)
        
    @classmethod
    def get_connection(cls):
        if cls._pool is None:
            cls.initialize()
        return cls._pool.connection()
    
    @classmethod
    def close_pool(cls) -> None:
        if cls._pool is not None:
            cls._pool.close()
            cls._pool = None

class MaintenanceTaskRepository:
    def find_by_id(self, task_id: int) -> MaintenanceTask | None:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT task_id, crew_id, intersection_id, task_type, status, scheduled_date, priority_level "
                    "FROM maintenance_task WHERE task_id = %s",
                    (task_id,),
                )
                row = cur.fetchone()
                return MaintenanceTask.from_row(row) if row else None

    def find_all(self, limit=20, offset=0) -> list[MaintenanceTask]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT task_id, crew_id, intersection_id, task_type, status, scheduled_date, priority_level "
                    "FROM maintenance_task ORDER BY task_id LIMIT %s OFFSET %s",
                    (limit, offset),
                )
                rows = cur.fetchall()
                return [MaintenanceTask.from_row(row) for row in rows]