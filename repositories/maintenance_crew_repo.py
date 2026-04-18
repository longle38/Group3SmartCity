from psycopg.rows import dict_row

from config.database import DatabaseConfig
from models.maintenance_crew import MaintenanceCrew


class MaintenanceCrewRepository:
    """Read-only access to maintenance_crew (GP2: partial/read-only is sufficient)."""

    def find_by_id(self, crew_id: int) -> MaintenanceCrew | None:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT crew_id, supervisor, specialization, certification_level, available
                    FROM maintenance_crew
                    WHERE crew_id = %s
                    """,
                    (crew_id,),
                )
                row = cur.fetchone()
                return MaintenanceCrew.from_row(row) if row else None

    def find_all(self, limit: int = 20, offset: int = 0) -> list[MaintenanceCrew]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT crew_id, supervisor, specialization, certification_level, available
                    FROM maintenance_crew
                    ORDER BY crew_id
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
                return [MaintenanceCrew.from_row(row) for row in cur.fetchall()]
