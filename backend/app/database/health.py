from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.session import engine


def check_database_connection() -> bool:
    """
    Verify that the application can successfully connect to PostgreSQL.

    Returns:
        True if the database connection succeeds.
        False if the connection fails.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True

    except SQLAlchemyError:
        return False