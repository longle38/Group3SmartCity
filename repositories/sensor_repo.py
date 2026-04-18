import os
import psycopg
import psycopg_pool
from dotenv import load_dotenv
from psycopg.rows import dict_row
from models.sensor import Sensor

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

class SensorRepository:
    def find_by_id(self, sensor_id: int) -> Sensor | None:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT sensor_id, intersection_id, sensor_type, installation_date, manufacturer, status "
                    "FROM sensor WHERE sensor_id = %s",
                    (sensor_id,),
                )
                row = cur.fetchone()
                return Sensor.from_row(row) if row else None
    def find_all(self, limit=20, offset=0) -> list[Sensor]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT sensor_id, intersection_id, sensor_type, installation_date, manufacturer, status "
                    "FROM sensor ORDER BY sensor_id LIMIT %s OFFSET %s",
                    (limit, offset),
                )
                return [Sensor.from_row(row) for row in cur.fetchall()]
    def find_by_manufacturer(self, manufacturer: str) -> list[Sensor]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT sensor_id, intersection_id, sensor_type, installation_date, manufacturer, status "
                    "FROM sensor WHERE manufacturer ILIKE %s ORDER BY installation_date DESC",
                    (f"%{manufacturer}%",),
                )
                return [Sensor.from_row(row) for row in cur.fetchall()]
    def find_by_intersection_id(self, intersection_id: int) -> list[Sensor]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT sensor_id, intersection_id, sensor_type, installation_date, manufacturer, status "
                    "FROM sensor WHERE intersection_id = %s ORDER BY installation_date DESC",
                    (intersection_id,),
                )
                return [Sensor.from_row(row) for row in cur.fetchall()]
    def find_by_status(self, status: str) -> list[Sensor]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT sensor_id, intersection_id, sensor_type, installation_date, manufacturer, status "
                    "FROM sensor WHERE status ILIKE %s ORDER BY installation_date DESC",
                    (f"%{status}%",),
                )
                return [Sensor.from_row(row) for row in cur.fetchall()]
    def count(self) -> int:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM sensor")
                row = cur.fetchone()
                return row[0] if row else 0
    def create(self, intersection_id: int, sensor_type: str, installation_date: str, manufacturer: str, status: str) -> int:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO sensor (intersection_id, sensor_type, installation_date, manufacturer, status) "
                    "VALUES (%s, %s, %s, %s, %s) "
                    "RETURNING sensor_id",
                    (intersection_id, sensor_type, installation_date, manufacturer, status),
                )
                row = cur.fetchone()
                conn.commit()
                return row[0]
    def update(self, sensor_id: int, intersection_id: int, sensor_type: str, installation_date: str, manufacturer: str, status: str) -> None:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE sensor SET intersection_id = %s, sensor_type = %s, installation_date = %s, manufacturer = %s, status = %s "
                    "WHERE sensor_id = %s",
                    (intersection_id, sensor_type, installation_date, manufacturer, status, sensor_id),
                )
                conn.commit()
    def delete(self, sensor_id: int) -> None:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM sensor WHERE sensor_id = %s",
                    (sensor_id,),
                )
                conn.commit()