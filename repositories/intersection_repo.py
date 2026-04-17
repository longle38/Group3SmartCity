from psycopg.rows import dict_row
from config.database import DatabaseConfig
from models.intersection import Intersection
from typing import Optional


class IntersectionRepository:
    """
    Full CRUD repository for the Intersection table.
    Contains only database operations — no business logic.
    """

    # ------------------------------------------------------------------
    # READ operations
    # ------------------------------------------------------------------

    def find_by_id(self, intersection_id: int) -> Optional[Intersection]:
        """Fetch a single intersection by its primary key. Returns None if not found."""
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT intersection_id, intersection_name,
                           longitude, latitude, intersection_type,
                           traffic_handling_capacity, installation_date,
                           jurisdictional_district, elevation,
                           created_at, updated_at
                    FROM intersection
                    WHERE intersection_id = %s
                    """,
                    (intersection_id,)
                )
                row = cur.fetchone()
                return Intersection.from_row(row) if row else None

    def find_all(self, limit: int = 20, offset: int = 0) -> list[Intersection]:
        """Fetch a paginated list of all intersections."""
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT intersection_id, intersection_name,
                           longitude, latitude, intersection_type,
                           traffic_handling_capacity, installation_date,
                           jurisdictional_district, elevation,
                           created_at, updated_at
                    FROM intersection
                    ORDER BY intersection_id
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset)
                )
                return [Intersection.from_row(row) for row in cur.fetchall()]

    def find_by_district(self, district: str) -> list[Intersection]:
        """Fetch all intersections within a specific jurisdictional district."""
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT intersection_id, intersection_name,
                           longitude, latitude, intersection_type,
                           traffic_handling_capacity, installation_date,
                           jurisdictional_district, elevation,
                           created_at, updated_at
                    FROM intersection
                    WHERE jurisdictional_district ILIKE %s
                    ORDER BY intersection_name
                    """,
                    (f"%{district}%",)
                )
                return [Intersection.from_row(row) for row in cur.fetchall()]

    def find_by_type(self, intersection_type: str) -> list[Intersection]:
        """Fetch all intersections of a specific type (e.g. '4-way', 'roundabout')."""
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT intersection_id, intersection_name,
                           longitude, latitude, intersection_type,
                           traffic_handling_capacity, installation_date,
                           jurisdictional_district, elevation,
                           created_at, updated_at
                    FROM intersection
                    WHERE intersection_type ILIKE %s
                    ORDER BY intersection_name
                    """,
                    (f"%{intersection_type}%",)
                )
                return [Intersection.from_row(row) for row in cur.fetchall()]

    def count(self) -> int:
        """Return the total number of intersections in the database."""
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM intersection")
                result = cur.fetchone()
                return result[0] if result else 0

    # ------------------------------------------------------------------
    # CREATE operation
    # ------------------------------------------------------------------

    def create(self, intersection: Intersection) -> Intersection:
        """
        Insert a new intersection into the database.
        Returns the same intersection with the newly assigned intersection_id.
        """
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    INSERT INTO intersection (
                        intersection_name, longitude, latitude,
                        intersection_type, traffic_handling_capacity,
                        installation_date, jurisdictional_district, elevation
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING intersection_id, intersection_name,
                              longitude, latitude, intersection_type,
                              traffic_handling_capacity, installation_date,
                              jurisdictional_district, elevation,
                              created_at, updated_at
                    """,
                    (
                        intersection.intersection_name,
                        intersection.longitude,
                        intersection.latitude,
                        intersection.intersection_type,
                        intersection.traffic_handling_capacity,
                        intersection.installation_date,
                        intersection.jurisdictional_district,
                        intersection.elevation,
                    )
                )
                row = cur.fetchone()
                return Intersection.from_row(row)

    # ------------------------------------------------------------------
    # UPDATE operation
    # ------------------------------------------------------------------

    def update(self, intersection: Intersection) -> Optional[Intersection]:
        """
        Update an existing intersection by its intersection_id.
        Returns the updated intersection, or None if the ID was not found.
        """
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    UPDATE intersection
                    SET intersection_name        = %s,
                        longitude                = %s,
                        latitude                 = %s,
                        intersection_type        = %s,
                        traffic_handling_capacity = %s,
                        installation_date        = %s,
                        jurisdictional_district  = %s,
                        elevation                = %s,
                        updated_at               = NOW()
                    WHERE intersection_id = %s
                    RETURNING intersection_id, intersection_name,
                              longitude, latitude, intersection_type,
                              traffic_handling_capacity, installation_date,
                              jurisdictional_district, elevation,
                              created_at, updated_at
                    """,
                    (
                        intersection.intersection_name,
                        intersection.longitude,
                        intersection.latitude,
                        intersection.intersection_type,
                        intersection.traffic_handling_capacity,
                        intersection.installation_date,
                        intersection.jurisdictional_district,
                        intersection.elevation,
                        intersection.intersection_id,
                    )
                )
                row = cur.fetchone()
                return Intersection.from_row(row) if row else None

    # ------------------------------------------------------------------
    # DELETE operation
    # ------------------------------------------------------------------

    def delete(self, intersection_id: int) -> bool:
        """
        Delete an intersection by its primary key.
        Returns True if a row was deleted, False if the ID was not found.
        """
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM intersection WHERE intersection_id = %s",
                    (intersection_id,)
                )
                return cur.rowcount > 0
