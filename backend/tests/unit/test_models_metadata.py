from app.database.base import Base

# Import all application models so their tables are registered
# with SQLAlchemy metadata.
import app.models  # noqa: F401


def test_all_expected_tables_are_registered() -> None:
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

    registered_tables = set(
        Base.metadata.tables.keys()
    )

    assert expected_tables == registered_tables