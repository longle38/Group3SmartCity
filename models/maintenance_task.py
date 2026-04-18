from dataclasses import dataclass
from datetime import date

@dataclass
class MaintenanceTask:
    task_id: int
    crew_id: int
    intersection_id: int
    task_type: str
    status: str
    scheduled_date: date
    priority_level: str
    
    @classmethod
    def from_row(cls, row: dict) -> "MaintenanceTask":
        """Convert a database row (dict) into a MaintenanceTask object."""
        return cls(
            task_id=row["task_id"],
            crew_id=row["crew_id"],
            intersection_id=row["intersection_id"],
            task_type=row["task_type"],
            status=row["status"],
            scheduled_date=row["scheduled_date"],
            priority_level=row["priority_level"]
        )

    def __str__(self) -> str:
        return (
            f"Maintenance Task #{self.task_id} assigned to Crew #{self.crew_id}:\n"
            f"  Intersection: {self.intersection_id}\n"
            f"  Type        : {self.task_type}\n"
            f"  Scheduled   : {self.scheduled_date}\n"
            f"  Status      : {self.status}\n"
            f"  Priority    : {self.priority_level}"
        )