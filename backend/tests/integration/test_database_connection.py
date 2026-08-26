from sqlalchemy import text

from app.database.session import engine


def test_database_connection():
    """
    Verify that SQLAlchemy can establish a connection to PostgreSQL
    and execute a basic SQL statement.
    """

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        assert result.scalar_one() == 1