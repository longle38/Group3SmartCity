import os
import psycopg
import psycopg_pool
from psycopg.rows import dict_row
from dotenv import load_dotenv
from models.traffic_signal import TrafficSignal

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

class TrafficSignalRepository:
    def find_by_id(self, signal_id: int) -> TrafficSignal | None:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT signal_id, intersection_id, signal_type, timing_mode, approach_direction, installation_date, power_source "
                    "FROM traffic_signal WHERE signal_id = %s",
                    (signal_id,),
                )
                row = cur.fetchone()
                return TrafficSignal.from_row(row) if row else None
    
    def find_all(self, limit=20, offset=0) -> list[TrafficSignal]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT signal_id, intersection_id, signal_type, timing_mode, approach_direction, installation_date, power_source "
                    "FROM traffic_signal ORDER BY signal_id LIMIT %s OFFSET %s",
                    (limit, offset),
                )
                rows = cur.fetchall()
                return [TrafficSignal.from_row(row) for row in rows]