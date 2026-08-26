from sqlalchemy import inspect

from app.database.session import engine


def test_expected_tables_exist():
    """
    Verify that the Alembic migration created every expected
    application table.
    """

    expected_tables = {
        "alembic_version",
        "programs",
        "locations",
        "field_officers",
        "raw_submissions",
        "activities",
        "program_targets",
        "data_quality_issues",
    }

    inspector = inspect(engine)

    actual_tables = set(
        inspector.get_table_names()
    )

    assert expected_tables.issubset(actual_tables)