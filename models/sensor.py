from dataclasses import dataclass
from datetime import date

@dataclass
class Sensor:
    sensor_id: int
    intersection_id: int
    sensor_type: str
    installation_date: date
    manufacturer: str
    status: str | None = None
    
    @classmethod
    def from_row(cls, row: dict) -> "Sensor":
        return cls(
            sensor_id=row["sensor_id"],
            intersection_id=row["intersection_id"],
            sensor_type=row["sensor_type"],
            installation_date=date.fromisoformat(row["installation_date"]),
            manufacturer=row["manufacturer"],
            status=row.get("status"),
        )
    
    def __str__(self) -> str:
        return (
            f"Sensor #{self.sensor_id}\n"
            f"  Type            : {self.sensor_type})\n"
            f"  Intersection ID : {self.intersection_id}\n"
            f"  Installed       : {self.installation_date}\n"
            f"  Manufacturer    : {self.manufacturer}\n"
            f"  Status          : {self.status or 'N/A'}"
        )