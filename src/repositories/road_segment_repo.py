import os
import psycopg
import psycopg_pool
from psycopg.rows import dict_row
from dotenv import load_dotenv
from models.road_segment import RoadSegment

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

class RoadSegmentRepository:
    def find_by_id(self, road_segment_id: int) -> RoadSegment | None:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT road_segment_id, start_intersection_id, end_intersection_id, surface_type, "
                    "number_of_lanes, lane_width, speed_limit, length, grade "
                    "FROM road_segment WHERE road_segment_id = %s",
                    (road_segment_id,),
                )
                row = cur.fetchone()
                return RoadSegment.from_row(row) if row else None
    
    def find_all(self, limit=20, offset=0) -> list[RoadSegment]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT road_segment_id, start_intersection_id, end_intersection_id, surface_type, "
                    "number_of_lanes, lane_width, speed_limit, length, grade "
                    "FROM road_segment ORDER BY road_segment_id LIMIT %s OFFSET %s",
                    (limit, offset),
                )
                rows = cur.fetchall()
                return [RoadSegment.from_row(row) for row in rows]