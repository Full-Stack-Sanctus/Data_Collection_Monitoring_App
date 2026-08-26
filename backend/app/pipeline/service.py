from pathlib import Path

from app.kobo.client import KoboClient
from app.pipeline.extractor import KoboSubmissionExtractor
from app.pipeline.validation import (
    SubmissionValidationService,
)
from app.schemas.pipeline import PipelineResult


class KoboPipelineService:
    """
    Coordinates the Kobo extraction and validation workflow.

    Current pipeline:

        Kobo API
            ↓
        Extract
            ↓
        Archive Raw Data
            ↓
        Transform + Validate
            ↓
        Accepted / Rejected Records

    Database loading will be added in a later phase.
    """

    def __init__(
        self,
        client: KoboClient,
        raw_data_directory: Path,
    ) -> None:
        self.extractor = KoboSubmissionExtractor(
            client=client,
            raw_data_directory=raw_data_directory,
        )

        self.validator = SubmissionValidationService()

    def run(
        self,
        asset_uid: str | None = None,
    ) -> tuple[PipelineResult, Path]:
        """
        Execute one extraction and validation pipeline run.

        Returns:
            - The validation result.
            - The location of the raw data archive.
        """

        raw_submissions = self.extractor.extract(
            asset_uid=asset_uid
        )

        archive_path = (
            self.extractor.archive_raw_submissions(
                raw_submissions
            )
        )

        result = self.validator.process(
            raw_submissions
        )

        return result, archive_path