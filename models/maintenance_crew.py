from dataclasses import dataclass
from typing import Any


@dataclass
class MaintenanceCrew:
    """Mirrors maintenance_crew in postgresql/schema.sql."""

    crew_id: int
    supervisor: str
    specialization: str
    certification_level: str
    available: bool

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "MaintenanceCrew":
        return cls(
            crew_id=row["crew_id"],
            supervisor=row["supervisor"],
            specialization=str(row["specialization"]),
            certification_level=row["certification_level"],
            available=bool(row["available"]),
        )

    def __str__(self) -> str:
        return (
            f"Maintenance crew #{self.crew_id}: {self.supervisor}\n"
            f"  Specialization : {self.specialization}\n"
            f"  Certification  : {self.certification_level}\n"
            f"  Available      : {self.available}"
        )
