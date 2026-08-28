from app.database.session import SessionLocal
from app.repositories.monitoring_repository import (
    MonitoringRepository,
)
from app.services.monitoring_service import (
    MonitoringService,
)


def main() -> None:
    """
    Retrieve and display the current monitoring aggregates.

    This script performs a lightweight post-pipeline verification
    against the monitoring service layer.
    """

    session = SessionLocal()

    try:
        repository = MonitoringRepository()
        service = MonitoringService(
            monitoring_repository=repository
        )

        print("\n=== MONITORING SUMMARY ===")

        summary = service.get_summary(
            session=session
        )

        print(summary)

        print("\n=== PROGRAM PERFORMANCE ===")

        program_performance = (
            service.get_program_performance(
                session=session
            )
        )

        for performance in program_performance:
            print(performance)

        print("\n=== GEOGRAPHIC PERFORMANCE ===")

        geographic_performance = (
            service.get_geographic_performance(
                session=session
            )
        )

        for performance in geographic_performance:
            print(performance)

        print("\n=== DATA QUALITY SUMMARY ===")

        data_quality_summary = (
            service.get_data_quality_summary(
                session=session
            )
        )

        print(data_quality_summary)

        print("\n=== DATA QUALITY ISSUE BREAKDOWN ===")

        issue_breakdown = (
            service.get_data_quality_issue_breakdown(
                session=session
            )
        )

        for issue in issue_breakdown:
            print(issue)

        print("\nMonitoring verification completed successfully.")

    finally:
        session.close()


if __name__ == "__main__":
    main()