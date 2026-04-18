from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Incident:
    """
    Mirrors the incident table in posgresql/schema.sql.
    PK: incident_number. At least one of intersection_id or road_segment_id is required on insert.
    """

    incident_type: str
    severity_level: str
    reporting_source: str
    reported_timestamp: datetime
    number_of_lanes_blocked: int

    incident_number: Optional[int] = None
    verified_timestamp: Optional[datetime] = None
    resolved_timestamp: Optional[datetime] = None
    intersection_id: Optional[int] = None
    road_segment_id: Optional[int] = None

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> Optional["Incident"]:
        if not row:
            return None
        return cls(
            incident_number=row.get("incident_number"),
            incident_type=row.get("incident_type"),
            severity_level=row.get("severity_level"),
            reporting_source=row.get("reporting_source"),
            reported_timestamp=row.get("reported_timestamp"),
            verified_timestamp=row.get("verified_timestamp"),
            resolved_timestamp=row.get("resolved_timestamp"),
            number_of_lanes_blocked=row.get("number_of_lanes_blocked"),
            intersection_id=row.get("intersection_id"),
            road_segment_id=row.get("road_segment_id"),
        )
