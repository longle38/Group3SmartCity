from typing import Any, List, Optional

from psycopg.rows import dict_row

from config.database import DatabaseConfig
from models.incident import Incident


class IncidentRepository:
    """
    Handles all database operations (CRUD) for the INCIDENT table.
    Contains NO business logic, only data access code utilizing the connection pool.
    """

    def find_by_id(self, incident_id: int) -> Optional[Incident]:
        """
        Retrieves a single incident by its primary key.
        """
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT incident_id, report_number, incident_type, severity_level,
                           status, reporting_source, reported_timestamp, verified_timestamp,
                           resolved_timestamp, lanes_blocked, intersection_id, road_segment_id
                    FROM incident
                    WHERE incident_id = %s;
                    """,
                    (incident_id,),
                )
                row = cur.fetchone()
                return Incident.from_row(row) if row else None

    def find_all(self, limit: int = 20, offset: int = 0) -> List[Incident]:
        """
        Retrieves a paginated list of incidents from the database.
        """
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT incident_id, report_number, incident_type, severity_level,
                           status, reporting_source, reported_timestamp, verified_timestamp,
                           resolved_timestamp, lanes_blocked, intersection_id, road_segment_id
                    FROM incident
                    ORDER BY reported_timestamp DESC
                    LIMIT %s OFFSET %s;
                    """,
                    (limit, offset),
                )
                return [Incident.from_row(row) for row in cur.fetchall()]

    def create(self, incident: Incident) -> Incident:
        """
        Inserts a new incident into the database and returns the object
        with its newly generated incident_id.
        """
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    INSERT INTO incident (
                        report_number, incident_type, severity_level, status,
                        reporting_source, reported_timestamp, verified_timestamp,
                        resolved_timestamp, lanes_blocked, intersection_id, road_segment_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING incident_id;
                    """,
                    (
                        incident.report_number,
                        incident.incident_type,
                        incident.severity_level,
                        incident.status,
                        incident.reporting_source,
                        incident.reported_timestamp,
                        incident.verified_timestamp,
                        incident.resolved_timestamp,
                        incident.lanes_blocked,
                        incident.intersection_id,
                        incident.road_segment_id,
                    ),
                )
                row = cur.fetchone()
                if row:
                    incident.incident_id = row["incident_id"]
            # psycopg3 auto-commits on clean exit of the context manager
            return incident

    def update(self, incident: Incident) -> None:
        """
        Updates an existing incident record.
        """
        if not incident.incident_id:
            raise ValueError("Cannot update an incident without an incident_id.")

        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE incident
                    SET report_number = %s,
                        incident_type = %s,
                        severity_level = %s,
                        status = %s,
                        reporting_source = %s,
                        reported_timestamp = %s,
                        verified_timestamp = %s,
                        resolved_timestamp = %s,
                        lanes_blocked = %s,
                        intersection_id = %s,
                        road_segment_id = %s
                    WHERE incident_id = %s;
                    """,
                    (
                        incident.report_number,
                        incident.incident_type,
                        incident.severity_level,
                        incident.status,
                        incident.reporting_source,
                        incident.reported_timestamp,
                        incident.verified_timestamp,
                        incident.resolved_timestamp,
                        incident.lanes_blocked,
                        incident.intersection_id,
                        incident.road_segment_id,
                        incident.incident_id,
                    ),
                )

    def delete(self, incident_id: int) -> None:
        """
        Deletes an incident from the database based on its ID.
        """
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM incident WHERE incident_id = %s;", (incident_id,)
                )

    def find_by_status(
        self, status: str, limit: int = 20, offset: int = 0
    ) -> List[Incident]:
        """
        Custom Query: Retrieves a paginated list of incidents by their operational status
        (e.g., 'active', 'cleared', 'investigating').
        """
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT incident_id, report_number, incident_type, severity_level,
                           status, reporting_source, reported_timestamp, verified_timestamp,
                           resolved_timestamp, lanes_blocked, intersection_id, road_segment_id
                    FROM incident
                    WHERE status = %s
                    ORDER BY reported_timestamp DESC
                    LIMIT %s OFFSET %s;
                    """,
                    (status, limit, offset),
                )
                return [Incident.from_row(row) for row in cur.fetchall()]

    def count_by_severity(self) -> List[dict[str, Any]]:
        """
        Analytics helper: incident counts grouped by severity_level.
        """
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT severity_level, COUNT(*)::bigint AS incident_count
                    FROM incident
                    GROUP BY severity_level
                    ORDER BY incident_count DESC, severity_level;
                    """
                )
                return list(cur.fetchall())
