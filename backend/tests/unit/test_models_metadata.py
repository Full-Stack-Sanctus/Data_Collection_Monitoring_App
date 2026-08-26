from app.database.base import Base

# Import all models so their tables are registered with SQLAlchemy metadata.
import app.database.models  # noqa: F401


def test_all_expected_tables_are_registered():
    """
    Verify that all ORM models are registered with SQLAlchemy metadata.
    """

    expected_tables = {
        "programs",
        "locations",
        "field_officers",
        "raw_submissions",
        "activities",
        "program_targets",
        "data_quality_issues",
    }

    registered_tables = set(Base.metadata.tables.keys())

    assert expected_tables == registered_tables