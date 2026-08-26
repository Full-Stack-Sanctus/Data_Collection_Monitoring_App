import json

from app.core.config import settings
from app.database.session import SessionLocal
from app.kobo.client import KoboAPIError, KoboClient
from app.pipeline.extractor import ExtractionError
from app.pipeline.report import DataQualityReporter
from app.pipeline.service import KoboPipelineService


def main() -> None:
    """
    Execute the complete Kobo extraction, validation, data quality,
    and database loading pipeline.
    """

    client = KoboClient()

    db = SessionLocal()

    try:
        pipeline = KoboPipelineService(
            client=client,
            raw_data_directory=(
                settings.raw_data_directory
            ),
        )

        (
            result,
            archive_path,
            database_result,
        ) = pipeline.run(
            session=db,
        )

        reporter = DataQualityReporter()

        quality_report = reporter.build_report(
            result
        )

        print("\nData Quality Report:")

        print(
            json.dumps(
                quality_report,
                indent=2,
            )
        )

        print("\nKobo Pipeline Completed\n")

        print(
            f"Total records extracted: "
            f"{result.total_records}"
        )

        print(
            f"Accepted records: "
            f"{result.accepted_count}"
        )

        print(
            f"Rejected records: "
            f"{result.rejected_count}"
        )

        print("\nDatabase Loading Results:")

        print(
            f"Accepted records inserted: "
            f"{database_result.accepted_inserted}"
        )

        print(
            f"Rejected records persisted: "
            f"{database_result.rejected_persisted}"
        )

        print(
            f"Skipped records: "
            f"{database_result.skipped_records}"
        )

        print(
            f"Database failures: "
            f"{database_result.failed_records}"
        )

        print(
            f"\nRaw archive: "
            f"{archive_path}"
        )

        if result.rejected_records:
            print(
                "\nRejected Submission Details:"
            )

            for rejected in result.rejected_records:
                print(
                    f"\nReference: "
                    f"{rejected.submission_reference}"
                )

                print(
                    f"Error: "
                    f"{rejected.error}"
                )

        if database_result.failures:
            print(
                "\nDatabase Failure Details:"
            )

            for failure in (
                database_result.failures
            ):
                print(
                    f"\nReference: "
                    f"{failure.submission_reference}"
                )

                print(
                    f"Error: "
                    f"{failure.error}"
                )

    except (
        KoboAPIError,
        ExtractionError,
    ) as error:
        print(
            "\nPipeline execution failed."
        )

        print(error)

    finally:
        db.close()

        client.close()


if __name__ == "__main__":
    main()