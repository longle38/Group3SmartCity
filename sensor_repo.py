from psycopg.rows import dict_row

from config.database import DatabaseConfig
from models.sensor import Sensor


class SensorRepository:
    """CRUD and lookups for sensor (posgresql/schema.sql)."""

    def find_by_id(self, sensor_id: int) -> Sensor | None:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT sensor_id, intersection_id, sensor_status, sensor_type,
                           installation_date
                    FROM sensor
                    WHERE sensor_id = %s
                    """,
                    (sensor_id,),
                )
                row = cur.fetchone()
                return Sensor.from_row(row) if row else None

    def find_all(self, limit: int = 20, offset: int = 0) -> list[Sensor]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT sensor_id, intersection_id, sensor_status, sensor_type,
                           installation_date
                    FROM sensor
                    ORDER BY sensor_id
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
                return [Sensor.from_row(row) for row in cur.fetchall()]

    def find_by_intersection_id(self, intersection_id: int) -> list[Sensor]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT sensor_id, intersection_id, sensor_status, sensor_type,
                           installation_date
                    FROM sensor
                    WHERE intersection_id = %s
                    ORDER BY installation_date DESC
                    """,
                    (intersection_id,),
                )
                return [Sensor.from_row(row) for row in cur.fetchall()]

    def find_by_sensor_status(self, sensor_status: str) -> list[Sensor]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT sensor_id, intersection_id, sensor_status, sensor_type,
                           installation_date
                    FROM sensor
                    WHERE sensor_status ILIKE %s
                    ORDER BY installation_date DESC
                    """,
                    (f"%{sensor_status}%",),
                )
                return [Sensor.from_row(row) for row in cur.fetchall()]

    def find_by_sensor_type(self, sensor_type: str) -> list[Sensor]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT sensor_id, intersection_id, sensor_status, sensor_type,
                           installation_date
                    FROM sensor
                    WHERE sensor_type::text ILIKE %s
                    ORDER BY installation_date DESC
                    """,
                    (f"%{sensor_type}%",),
                )
                return [Sensor.from_row(row) for row in cur.fetchall()]

    def count(self) -> int:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM sensor")
                row = cur.fetchone()
                return row[0] if row else 0

    def create(
        self,
        intersection_id: int,
        sensor_status: str,
        sensor_type: str,
        installation_date: str,
    ) -> int:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sensor (
                        intersection_id, sensor_status, sensor_type, installation_date
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING sensor_id
                    """,
                    (intersection_id, sensor_status, sensor_type, installation_date),
                )
                row = cur.fetchone()
                return row[0]

    def update(
        self,
        sensor_id: int,
        intersection_id: int,
        sensor_status: str,
        sensor_type: str,
        installation_date: str,
    ) -> None:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE sensor
                    SET intersection_id = %s,
                        sensor_status = %s,
                        sensor_type = %s,
                        installation_date = %s
                    WHERE sensor_id = %s
                    """,
                    (
                        intersection_id,
                        sensor_status,
                        sensor_type,
                        installation_date,
                        sensor_id,
                    ),
                )

    def delete(self, sensor_id: int) -> None:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM sensor WHERE sensor_id = %s", (sensor_id,))
