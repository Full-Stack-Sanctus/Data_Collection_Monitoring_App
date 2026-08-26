from pathlib import Path

from sqlalchemy.orm import Session

from app.kobo.client import KoboClient
from app.pipeline.extractor import KoboSubmissionExtractor
from app.pipeline.validation import (
    SubmissionValidationService,
)
from app.schemas.load_result import DatabaseLoadResult
from app.schemas.pipeline import PipelineResult
from app.services.submission_loader import (
    SubmissionLoader,
)


class KoboPipelineService:
    """
    Coordinates the complete Kobo data pipeline.

    Pipeline:

        Kobo API
            ↓
        Extract
            ↓
        Archive Raw Data
            ↓
        Transform + Validate
            ↓
        PipelineResult
            ↓
        PostgreSQL Loading
            ↓
        Normalized Database Records
    """

    def __init__(
        self,
        client: KoboClient,
        raw_data_directory: Path,
        submission_loader: (
            SubmissionLoader | None
        ) = None,
    ) -> None:
        self.extractor = KoboSubmissionExtractor(
            client=client,
            raw_data_directory=raw_data_directory,
        )

        self.validator = SubmissionValidationService()

        self.submission_loader = (
            submission_loader
            or SubmissionLoader()
        )

    def run(
        self,
        *,
        session: Session,
        asset_uid: str | None = None,
    ) -> tuple[
        PipelineResult,
        Path,
        DatabaseLoadResult,
    ]:
        """
        Execute one complete Kobo pipeline run.

        Returns:

            - Validation result.
            - Raw archive path.
            - Database loading result.
        """

        raw_submissions = self.extractor.extract(
            asset_uid=asset_uid
        )

        archive_path = (
            self.extractor.archive_raw_submissions(
                raw_submissions
            )
        )

        pipeline_result = self.validator.process(
            raw_submissions
        )

        database_result = (
            self.submission_loader.load(
                session=session,
                pipeline_result=pipeline_result,
            )
        )

        return (
            pipeline_result,
            archive_path,
            database_result,
        )