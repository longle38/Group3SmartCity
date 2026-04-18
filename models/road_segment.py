from dataclasses import dataclass

@dataclass
class RoadSegment:
    road_segment_id: int
    start_intersection_id: int
    end_intersection_id: int
    surface_type: str
    number_of_lanes: int
    lane_width: float
    speed_limit: int
    length: float
    grade: float

    @classmethod
    def from_row(cls, row: dict) -> "RoadSegment":
        return cls(
            road_segment_id=row["road_segment_id"],
            start_intersection_id=row["start_intersection_id"],
            end_intersection_id=row["end_intersection_id"],
            surface_type=row["surface_type"],
            number_of_lanes=row["number_of_lanes"],
            lane_width=row["lane_width"],
            speed_limit=row["speed_limit"],
            length=row["length"],
            grade=row["grade"],
        )
    
    def __str__(self) -> str:
        return (
            f"Road Segment #{self.road_segment_id}\n"
            f"  Start Intersection ID : {self.start_intersection_id}\n"
            f"  End Intersection ID   : {self.end_intersection_id}\n"
            f"  Surface Type         : {self.surface_type}\n"
            f"  Number of Lanes      : {self.number_of_lanes}\n"
            f"  Lane Width           : {self.lane_width} m\n"
            f"  Speed Limit          : {self.speed_limit} km/h\n"
            f"  Length               : {self.length} m\n"
            f"  Grade                : {self.grade}%"
        )