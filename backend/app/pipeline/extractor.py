import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.kobo.client import KoboClient


class ExtractionError(Exception):
    """
    Raised when Kobo submissions cannot be extracted or archived.
    """

    pass


class KoboSubmissionExtractor:
    """
    Responsible for extracting raw submissions from KoboToolbox.

    Responsibilities:
    - Retrieve all available submissions.
    - Preserve the raw response.
    - Return the raw submissions for further validation.
    """

    def __init__(
        self,
        client: KoboClient,
        raw_data_directory: Path,
    ) -> None:
        self.client = client
        self.raw_data_directory = raw_data_directory

    def extract(
        self,
        asset_uid: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve all submissions from KoboToolbox.

        Raw records are returned exactly as received from the
        Kobo client.
        """

        try:
            return self.client.get_all_submissions(
                asset_uid=asset_uid
            )

        except Exception as error:
            raise ExtractionError(
                "Failed to extract submissions from KoboToolbox."
            ) from error

    def archive_raw_submissions(
        self,
        submissions: list[dict[str, Any]],
    ) -> Path:
        """
        Save the complete raw submission batch to a timestamped
        JSON file.

        The archive allows us to:
        - investigate validation failures;
        - reproduce pipeline results;
        - reprocess data;
        - avoid losing the original external payload.
        """

        try:
            self.raw_data_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            archive_path = (
                self.raw_data_directory
                / f"kobo_submissions_{timestamp}.json"
            )

            payload = {
                "extracted_at": datetime.now().isoformat(),
                "record_count": len(submissions),
                "submissions": submissions,
            }

            with archive_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    payload,
                    file,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )

            return archive_path

        except OSError as error:
            raise ExtractionError(
                "Failed to archive raw Kobo submissions."
            ) from error