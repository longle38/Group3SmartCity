"""
Business logic for the CLI: combines repositories and cross-table reads.
"""

from __future__ import annotations

from typing import Any, List, Optional

import psycopg
from psycopg.rows import dict_row

from config.database import DatabaseConfig
from models.intersection import Intersection
from repositories.postgres.incident_repo import IncidentRepository
from repositories.postgres.intersection_repo import IntersectionRepository


class TrafficService:
    def __init__(self) -> None:
        self._intersections = IntersectionRepository()
        self._incidents = IncidentRepository()

    def get_intersection_by_id(self, intersection_id: int) -> Optional[Intersection]:
        return self._intersections.find_by_id(intersection_id)

    def get_high_incident_intersections(self, limit: int = 20) -> List[dict[str, Any]]:
        """
        Intersections ranked by incident count in the last 90 days, with sensor counts.
        Uses subqueries so incident rows do not inflate sensor counts.
        """
        sql = """
        SELECT
            i.intersection_id,
            i.intersection_name,
            i.jurisdiction_district AS zone,
            COALESCE(inc_stats.incident_count, 0)::bigint AS incidents,
            COALESCE(sens.sensor_count, 0)::bigint AS sensors
        FROM intersection i
        LEFT JOIN (
            SELECT intersection_id, COUNT(*)::bigint AS incident_count
            FROM incident
            WHERE intersection_id IS NOT NULL
              AND reported_timestamp >= NOW() - INTERVAL '90 days'
            GROUP BY intersection_id
        ) inc_stats ON inc_stats.intersection_id = i.intersection_id
        LEFT JOIN (
            SELECT intersection_id, COUNT(*)::bigint AS sensor_count
            FROM sensor
            GROUP BY intersection_id
        ) sens ON sens.intersection_id = i.intersection_id
        ORDER BY COALESCE(inc_stats.incident_count, 0) DESC, i.intersection_name
        LIMIT %(limit)s;
        """
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(sql, {"limit": limit})
                return list(cur.fetchall())

    def get_system_metrics(self) -> dict[str, Any]:
        """Totals used for the analytics menu (best-effort for maintenance_task)."""
        metrics: dict[str, Any] = {}
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*)::bigint FROM incident")
                metrics["total_incidents"] = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*)::bigint FROM intersection")
                n_int = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*)::bigint FROM sensor")
                n_sens = cur.fetchone()[0]
                metrics["total_intersections"] = n_int
                metrics["total_sensors"] = n_sens
                metrics["avg_sensors_per_intersection"] = (
                    float(n_sens) / float(n_int) if n_int else 0.0
                )
                try:
                    cur.execute(
                        """
                        SELECT COUNT(*)::bigint
                        FROM maintenance_task
                        WHERE maintenance_status::text NOT IN ('completed');
                        """
                    )
                    row = cur.fetchone()
                    metrics["open_maintenance_tasks"] = (
                        int(row[0]) if row else 0
                    )
                except psycopg.Error:
                    metrics["open_maintenance_tasks"] = None
        return metrics

    def get_incident_counts_by_severity(self) -> List[dict[str, Any]]:
        return self._incidents.count_by_severity()
