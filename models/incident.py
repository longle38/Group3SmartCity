from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Incident:
    """
    Data model representing a traffic incident.
    Mirrors the INCIDENT table in the database.
    """

    report_number: str
    incident_type: str
    severity_level: str
    status: str
    reporting_source: str
    reported_timestamp: datetime
    lanes_blocked: int

    # incident_id is Optional because it won't exist until the DB generates it
    incident_id: Optional[int] = None

    # Nullable fields
    verified_timestamp: Optional[datetime] = None
    resolved_timestamp: Optional[datetime] = None

    # FKs are nullable because of the XOR constraint (it's at one or the other, not both)
    intersection_id: Optional[int] = None
    road_segment_id: Optional[int] = None

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> Optional["Incident"]:
        """
        Converts a raw database dict_row into an Incident object.
        Assumes row_factory=dict_row is used in psycopg3.
        """
        if not row:
            return None

        return cls(
            incident_id=row.get("incident_id"),
            report_number=row.get("report_number"),
            incident_type=row.get("incident_type"),
            severity_level=row.get("severity_level"),
            status=row.get("status"),
            reporting_source=row.get("reporting_source"),
            reported_timestamp=row.get("reported_timestamp"),
            verified_timestamp=row.get("verified_timestamp"),
            resolved_timestamp=row.get("resolved_timestamp"),
            lanes_blocked=row.get("lanes_blocked"),
            intersection_id=row.get("intersection_id"),
            road_segment_id=row.get("road_segment_id"),
        )
