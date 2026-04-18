from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Sensor:
    """Mirrors sensor in posgresql/schema.sql (signalized intersections only)."""

    sensor_id: int
    intersection_id: int
    sensor_status: str
    sensor_type: str
    installation_date: date

    @classmethod
    def from_row(cls, row: dict) -> "Sensor":
        raw_install = row["installation_date"]
        if isinstance(raw_install, datetime):
            inst_date: date = raw_install.date()
        elif isinstance(raw_install, date):
            inst_date = raw_install
        else:
            inst_date = date.fromisoformat(str(raw_install))
        return cls(
            sensor_id=row["sensor_id"],
            intersection_id=row["intersection_id"],
            sensor_status=row["sensor_status"],
            sensor_type=row["sensor_type"],
            installation_date=inst_date,
        )

    def __str__(self) -> str:
        return (
            f"Sensor #{self.sensor_id}\n"
            f"  Type             : {self.sensor_type}\n"
            f"  Intersection ID  : {self.intersection_id}\n"
            f"  Installed        : {self.installation_date}\n"
            f"  Status           : {self.sensor_status}"
        )
