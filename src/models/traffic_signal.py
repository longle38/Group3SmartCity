from dataclasses import dataclass
from datetime import date

@dataclass
class TrafficSignal:
    signal_id: int
    intersection_id: int
    signal_type: str
    timing_mode: str
    approach_direction: str
    installation_date: date
    power_source: str

    @classmethod
    def from_row(cls, row: dict) -> "TrafficSignal":
        return cls(
            signal_id=row["signal_id"],
            intersection_id=row["intersection_id"],
            signal_type=row["signal_type"],
            timing_mode=row["timing_mode"],
            approach_direction=row["approach_direction"],
            installation_date=date.fromisoformat(row["installation_date"]),
            power_source=row["power_source"],
        )
    
    def __str__(self) -> str:
        return (
            f"Traffic Signal #{self.signal_id}\n"
            f"  Intersection ID : {self.intersection_id}\n"
            f"  Type            : {self.signal_type}\n"
            f"  Timing Mode     : {self.timing_mode}\n"
            f"  Approach        : {self.approach_direction}\n"
            f"  Installation Date : {self.installation_date}\n"
            f"  Power Source    : {self.power_source}"
        )