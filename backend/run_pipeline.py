from app.core.config import settings
from app.kobo.client import KoboAPIError, KoboClient
from app.pipeline.extractor import ExtractionError
from app.pipeline.service import KoboPipelineService

import json

from app.pipeline.report import DataQualityReporter


def main() -> None:
    """
    Execute the Kobo extraction and validation pipeline.
    """

    client = KoboClient()

    try:
        pipeline = KoboPipelineService(
            client=client,
            raw_data_directory=(
                settings.raw_data_directory
            ),
        )

        result, archive_path = pipeline.run()
        
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
            f"Total records: "
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

    except (
        KoboAPIError,
        ExtractionError,
    ) as error:
        print(
            "\nPipeline execution failed."
        )

        print(error)

    finally:
        client.close()


if __name__ == "__main__":
    main()