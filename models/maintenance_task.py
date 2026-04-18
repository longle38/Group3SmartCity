from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional


@dataclass
class MaintenanceTask:
    """
    Mirrors maintenance_task in postgresql/schema.sql.
    Links to assets (sensor, signal, etc.) are via junction tables, not intersection_id on this row.
    """

    maintenance_status: str
    maintenance_type: str
    estimated_duration_minutes: int
    priority_level: str
    task_id: Optional[int] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[datetime] = None
    assigned_crew: Optional[int] = None
    actual_duration_minutes: Optional[int] = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "MaintenanceTask":
        raw_date = row.get("scheduled_date")
        if isinstance(raw_date, datetime):
            sched_date: Optional[date] = raw_date.date()
        elif isinstance(raw_date, date):
            sched_date = raw_date
        elif raw_date is None:
            sched_date = None
        else:
            sched_date = date.fromisoformat(str(raw_date)[:10])

        raw_ts = row.get("scheduled_time")
        if isinstance(raw_ts, datetime):
            sched_time: Optional[datetime] = raw_ts
        elif raw_ts is None:
            sched_time = None
        else:
            s = str(raw_ts)[:19]
            sched_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

        return cls(
            task_id=row.get("task_id"),
            maintenance_status=str(row["maintenance_status"]),
            maintenance_type=str(row["maintenance_type"]),
            scheduled_date=sched_date,
            scheduled_time=sched_time,
            estimated_duration_minutes=int(row["estimated_duration_minutes"]),
            priority_level=str(row["priority_level"]),
            assigned_crew=row.get("assigned_crew"),
            actual_duration_minutes=(
                int(row["actual_duration_minutes"])
                if row.get("actual_duration_minutes") is not None
                else None
            ),
        )

    def __str__(self) -> str:
        return (
            f"Maintenance task #{self.task_id}\n"
            f"  Status       : {self.maintenance_status}\n"
            f"  Type         : {self.maintenance_type}\n"
            f"  Scheduled    : {self.scheduled_date} {self.scheduled_time or ''}\n"
            f"  Est. minutes : {self.estimated_duration_minutes}\n"
            f"  Priority     : {self.priority_level}\n"
            f"  Crew         : {self.assigned_crew}\n"
            f"  Actual min.  : {self.actual_duration_minutes}"
        )
