from app.database.session import SessionLocal
from app.repositories.monitoring_repository import (
    MonitoringRepository,
)


def main() -> None:
    """
    Retrieve and display the current monitoring aggregates.
    """

    session = SessionLocal()

    try:
        repository = MonitoringRepository()

        summary = repository.get_summary(
            session
        )

        print(summary)

    finally:
        session.close()


if __name__ == "__main__":
    main()