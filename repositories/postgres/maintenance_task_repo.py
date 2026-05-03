from psycopg.rows import dict_row

from config.database import DatabaseConfig
from models.maintenance_task import MaintenanceTask


class MaintenanceTaskRepository:
    """Read-only access to maintenance_task (GP2: partial/read-only is sufficient)."""

    def find_by_id(self, task_id: int) -> MaintenanceTask | None:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT task_id, maintenance_status, maintenance_type, scheduled_date,
                           scheduled_time, estimated_duration_minutes, priority_level,
                           assigned_crew, actual_duration_minutes
                    FROM maintenance_task
                    WHERE task_id = %s
                    """,
                    (task_id,),
                )
                row = cur.fetchone()
                return MaintenanceTask.from_row(row) if row else None

    def find_all(self, limit: int = 20, offset: int = 0) -> list[MaintenanceTask]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT task_id, maintenance_status, maintenance_type, scheduled_date,
                           scheduled_time, estimated_duration_minutes, priority_level,
                           assigned_crew, actual_duration_minutes
                    FROM maintenance_task
                    ORDER BY task_id
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
                return [MaintenanceTask.from_row(row) for row in cur.fetchall()]
