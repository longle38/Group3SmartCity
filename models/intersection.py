from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Intersection:
    intersection_id: int
    intersection_name: str
    longitude: float
    latitude: float
    intersection_type: Optional[str]
    traffic_handling_capacity: Optional[int]
    installation_date: Optional[date]
    jurisdictional_district: Optional[str]
    elevation: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @classmethod
    def from_row(cls, row: dict) -> "Intersection":
        """Convert a database row (dict) into an Intersection object."""
        return cls(
            intersection_id=row["intersection_id"],
            intersection_name=row["intersection_name"],
            longitude=float(row["longitude"]),
            latitude=float(row["latitude"]),
            intersection_type=row.get("intersection_type"),
            traffic_handling_capacity=row.get("traffic_handling_capacity"),
            installation_date=row.get("installation_date"),
            jurisdictional_district=row.get("jurisdictional_district"),
            elevation=float(row["elevation"]) if row.get("elevation") is not None else None,
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def __str__(self) -> str:
        return (
            f"Intersection #{self.intersection_id}: {self.intersection_name}\n"
            f"  Location   : ({self.latitude}, {self.longitude})\n"
            f"  Type       : {self.intersection_type or 'N/A'}\n"
            f"  Capacity   : {self.traffic_handling_capacity or 'N/A'} vehicles/hr\n"
            f"  District   : {self.jurisdictional_district or 'N/A'}\n"
            f"  Elevation  : {self.elevation or 'N/A'} m\n"
            f"  Installed  : {self.installation_date or 'N/A'}"
        )
