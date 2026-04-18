from dataclasses import dataclass

@dataclass
class MaintenanceCrew:
    crew_id: int
    crew_name: str
    
    @classmethod
    def from_row(cls, row: dict) -> "MaintenanceCrew":
        """Convert a database row (dict) into a MaintenanceCrew object."""
        return cls(
            crew_id=row["crew_id"],
            crew_name=row["crew_name"]
        )

    def __str__(self) -> str:
        return (
            f"Maintenance Crew #{self.crew_id}: {self.crew_name}\n"
        )