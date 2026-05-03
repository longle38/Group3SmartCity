from typing import Any, List, Optional

from psycopg.rows import dict_row

from config.database import DatabaseConfig
from models.incident import Incident


class IncidentRepository:
    """
    CRUD for the incident table (schema: posgresql/schema.sql).
    No business logic.
    """

    def find_by_id(self, incident_number: int) -> Optional[Incident]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT incident_number, incident_type, severity_level,
                           reporting_source, reported_timestamp, verified_timestamp,
                           resolved_timestamp, number_of_lanes_blocked,
                           intersection_id, road_segment_id
                    FROM incident
                    WHERE incident_number = %s;
                    """,
                    (incident_number,),
                )
                row = cur.fetchone()
                return Incident.from_row(row) if row else None

    def find_all(self, limit: int = 20, offset: int = 0) -> List[Incident]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT incident_number, incident_type, severity_level,
                           reporting_source, reported_timestamp, verified_timestamp,
                           resolved_timestamp, number_of_lanes_blocked,
                           intersection_id, road_segment_id
                    FROM incident
                    ORDER BY reported_timestamp DESC
                    LIMIT %s OFFSET %s;
                    """,
                    (limit, offset),
                )
                return [Incident.from_row(row) for row in cur.fetchall()]

    def create(self, incident: Incident) -> Incident:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    INSERT INTO incident (
                        incident_type, severity_level, reporting_source,
                        reported_timestamp, verified_timestamp, resolved_timestamp,
                        number_of_lanes_blocked, intersection_id, road_segment_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING incident_number;
                    """,
                    (
                        incident.incident_type,
                        incident.severity_level,
                        incident.reporting_source,
                        incident.reported_timestamp,
                        incident.verified_timestamp,
                        incident.resolved_timestamp,
                        incident.number_of_lanes_blocked,
                        incident.intersection_id,
                        incident.road_segment_id,
                    ),
                )
                row = cur.fetchone()
                if row:
                    incident.incident_number = row["incident_number"]
            return incident

    def update(self, incident: Incident) -> None:
        if not incident.incident_number:
            raise ValueError("Cannot update an incident without incident_number.")

        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE incident
                    SET incident_type = %s,
                        severity_level = %s,
                        reporting_source = %s,
                        reported_timestamp = %s,
                        verified_timestamp = %s,
                        resolved_timestamp = %s,
                        number_of_lanes_blocked = %s,
                        intersection_id = %s,
                        road_segment_id = %s
                    WHERE incident_number = %s;
                    """,
                    (
                        incident.incident_type,
                        incident.severity_level,
                        incident.reporting_source,
                        incident.reported_timestamp,
                        incident.verified_timestamp,
                        incident.resolved_timestamp,
                        incident.number_of_lanes_blocked,
                        incident.intersection_id,
                        incident.road_segment_id,
                        incident.incident_number,
                    ),
                )

    def delete(self, incident_number: int) -> None:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM incident WHERE incident_number = %s;",
                    (incident_number,),
                )

    def find_by_severity(
        self, severity_level: str, limit: int = 20, offset: int = 0
    ) -> List[Incident]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT incident_number, incident_type, severity_level,
                           reporting_source, reported_timestamp, verified_timestamp,
                           resolved_timestamp, number_of_lanes_blocked,
                           intersection_id, road_segment_id
                    FROM incident
                    WHERE severity_level::text = %s
                    ORDER BY reported_timestamp DESC
                    LIMIT %s OFFSET %s;
                    """,
                    (severity_level, limit, offset),
                )
                return [Incident.from_row(row) for row in cur.fetchall()]

    def count_by_severity(self) -> List[dict[str, Any]]:
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT severity_level::text AS severity_level,
                           COUNT(*)::bigint AS incident_count
                    FROM incident
                    GROUP BY severity_level
                    ORDER BY incident_count DESC, severity_level;
                    """
                )
                return list(cur.fetchall())
