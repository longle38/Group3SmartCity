"""
Tests for IntersectionRepository (full CRUD).

How to run:
    1. Make sure your .env file is set up with real DB credentials
    2. Make sure schema.sql and data.sql have been loaded into PostgreSQL
    3. From the traffic-management/ root folder, run:
           pip install psycopg[binary] psycopg_pool python-dotenv
           python -m pytest tests/test_intersection_repo.py -v

These are integration tests — they hit the real database.
Each test cleans up after itself so it does not leave junk data.
"""

import pytest
from datetime import date
from models.intersection import Intersection
from repositories.intersection_repo import IntersectionRepository
from config.database import DatabaseConfig


# ------------------------------------------------------------------
# Setup: initialize the DB pool once for the whole test session
# ------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def init_db():
    """Start the connection pool before tests, close it after."""
    DatabaseConfig.initialize()
    yield
    DatabaseConfig.close_all()


@pytest.fixture
def repo():
    """Return a fresh IntersectionRepository for each test."""
    return IntersectionRepository()


@pytest.fixture
def sample_intersection():
    """A sample Intersection object used for create/update/delete tests."""
    return Intersection(
        intersection_id=None,           # DB assigns this on INSERT
        intersection_name="Test St & Sample Ave",
        longitude=-73.985130,
        latitude=40.758896,
        intersection_type="4-way",
        traffic_handling_capacity=800,
        installation_date=date(2020, 6, 15),
        jurisdictional_district="Downtown",
        elevation=12.50,
        created_at=None,
        updated_at=None,
    )


# ------------------------------------------------------------------
# READ tests
# ------------------------------------------------------------------

class TestFindAll:
    def test_returns_a_list(self, repo):
        """find_all() should always return a list (even if empty)."""
        results = repo.find_all()
        assert isinstance(results, list)

    def test_respects_limit(self, repo):
        """find_all() should return no more rows than the limit."""
        results = repo.find_all(limit=5)
        assert len(results) <= 5

    def test_each_item_is_intersection(self, repo):
        """Every item returned should be an Intersection object."""
        results = repo.find_all(limit=10)
        for item in results:
            assert isinstance(item, Intersection)

    def test_pagination_offset(self, repo):
        """Results with offset should differ from results without offset."""
        page1 = repo.find_all(limit=5, offset=0)
        page2 = repo.find_all(limit=5, offset=5)
        if len(page1) == 5 and len(page2) > 0:
            assert page1[0].intersection_id != page2[0].intersection_id


class TestFindById:
    def test_returns_none_for_missing_id(self, repo):
        """find_by_id() with a non-existent ID should return None."""
        result = repo.find_by_id(999999)
        assert result is None

    def test_returns_correct_intersection(self, repo):
        """find_by_id() should return the intersection with the matching ID."""
        all_intersections = repo.find_all(limit=1)
        if not all_intersections:
            pytest.skip("No data in database yet")
        first = all_intersections[0]
        found = repo.find_by_id(first.intersection_id)
        assert found is not None
        assert found.intersection_id == first.intersection_id
        assert found.intersection_name == first.intersection_name


class TestFindByDistrict:
    def test_returns_list(self, repo):
        """find_by_district() should return a list."""
        results = repo.find_by_district("Downtown")
        assert isinstance(results, list)

    def test_all_results_match_district(self, repo):
        """Every result should belong to the searched district."""
        results = repo.find_by_district("Downtown")
        for item in results:
            assert "downtown" in item.jurisdictional_district.lower()


class TestCount:
    def test_count_is_non_negative(self, repo):
        """count() should return a non-negative integer."""
        total = repo.count()
        assert isinstance(total, int)
        assert total >= 0


# ------------------------------------------------------------------
# CREATE test
# ------------------------------------------------------------------

class TestCreate:
    def test_create_returns_intersection_with_id(self, repo, sample_intersection):
        """create() should return the saved intersection with a real DB-assigned ID."""
        created = repo.create(sample_intersection)

        # Cleanup first in case asserts fail
        try:
            assert created is not None
            assert created.intersection_id is not None
            assert created.intersection_id > 0
            assert created.intersection_name == sample_intersection.intersection_name
            assert float(created.latitude) == sample_intersection.latitude
            assert float(created.longitude) == sample_intersection.longitude
        finally:
            repo.delete(created.intersection_id)

    def test_created_intersection_is_retrievable(self, repo, sample_intersection):
        """After create(), find_by_id() should find the new record."""
        created = repo.create(sample_intersection)
        try:
            found = repo.find_by_id(created.intersection_id)
            assert found is not None
            assert found.intersection_name == sample_intersection.intersection_name
        finally:
            repo.delete(created.intersection_id)


# ------------------------------------------------------------------
# UPDATE test
# ------------------------------------------------------------------

class TestUpdate:
    def test_update_changes_fields(self, repo, sample_intersection):
        """update() should persist changes to the database."""
        created = repo.create(sample_intersection)
        try:
            created.intersection_name = "Updated St & New Ave"
            created.traffic_handling_capacity = 1200
            updated = repo.update(created)

            assert updated is not None
            assert updated.intersection_name == "Updated St & New Ave"
            assert updated.traffic_handling_capacity == 1200
        finally:
            repo.delete(created.intersection_id)

    def test_update_nonexistent_returns_none(self, repo, sample_intersection):
        """update() on a non-existent ID should return None."""
        sample_intersection.intersection_id = 999999
        result = repo.update(sample_intersection)
        assert result is None

    def test_update_reflects_in_find_by_id(self, repo, sample_intersection):
        """After update(), find_by_id() should return the updated values."""
        created = repo.create(sample_intersection)
        try:
            created.jurisdictional_district = "Industrial"
            repo.update(created)
            found = repo.find_by_id(created.intersection_id)
            assert found.jurisdictional_district == "Industrial"
        finally:
            repo.delete(created.intersection_id)


# ------------------------------------------------------------------
# DELETE test
# ------------------------------------------------------------------

class TestDelete:
    def test_delete_returns_true_for_existing(self, repo, sample_intersection):
        """delete() should return True when a record is successfully deleted."""
        created = repo.create(sample_intersection)
        result = repo.delete(created.intersection_id)
        assert result is True

    def test_delete_returns_false_for_missing(self, repo):
        """delete() should return False when the ID does not exist."""
        result = repo.delete(999999)
        assert result is False

    def test_deleted_record_not_findable(self, repo, sample_intersection):
        """After delete(), find_by_id() should return None."""
        created = repo.create(sample_intersection)
        repo.delete(created.intersection_id)
        found = repo.find_by_id(created.intersection_id)
        assert found is None
