from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional


@dataclass
class Intersection:
    """Mirrors intersection in posgresql/schema.sql."""

    intersection_name: str
    latitude: float
    longitude: float
    intersection_type: str
    traffic_handling_capacity: int
    installation_date: date
    jurisdiction_district: str
    elevation: float
    intersection_id: Optional[int] = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "Intersection":
        raw_install = row["installation_date"]
        if isinstance(raw_install, datetime):
            inst: date = raw_install.date()
        elif isinstance(raw_install, date):
            inst = raw_install
        else:
            inst = date.fromisoformat(str(raw_install)[:10])

        def _f(val: Any) -> float:
            return float(val)

        return cls(
            intersection_id=row["intersection_id"],
            intersection_name=row["intersection_name"],
            latitude=_f(row["latitude"]),
            longitude=_f(row["longitude"]),
            intersection_type=str(row["intersection_type"]),
            traffic_handling_capacity=int(row["traffic_handling_capacity"]),
            installation_date=inst,
            jurisdiction_district=str(row["jurisdiction_district"]),
            elevation=_f(row["elevation"]),
        )

    def __str__(self) -> str:
        return (
            f"Intersection #{self.intersection_id}: {self.intersection_name}\n"
            f"  Location   : ({self.latitude}, {self.longitude})\n"
            f"  Type       : {self.intersection_type}\n"
            f"  Capacity   : {self.traffic_handling_capacity} vehicles/hr\n"
            f"  District   : {self.jurisdiction_district}\n"
            f"  Elevation  : {self.elevation} m\n"
            f"  Installed  : {self.installation_date}"
        )
