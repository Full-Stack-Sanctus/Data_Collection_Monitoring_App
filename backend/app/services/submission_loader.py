from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.activity import Activity

from app.repositories.data_quality_issue_repository import (
    DataQualityIssueRepository,
)
from app.repositories.field_officer_repository import (
    FieldOfficerRepository,
)
from app.repositories.location_repository import (
    LocationRepository,
)
from app.repositories.program_repository import (
    ProgramRepository,
)
from app.repositories.raw_submission_repository import (
    RawSubmissionRepository,
)

from app.schemas.kobo_submission import KoboSubmission
from app.schemas.load_result import (
    DatabaseLoadResult,
    LoadFailure,
)
from app.schemas.pipeline import (
    AcceptedSubmission,
    PipelineResult,
    RejectedSubmission,
)


class SubmissionLoader:
    """
    Loads validated and rejected Kobo submissions into the
    application's PostgreSQL database.

    Accepted records:

        RawSubmission
            ↓
        Program
        Location
        FieldOfficer
            ↓
        Activity

    Rejected records:

        RawSubmission
            ↓
        DataQualityIssue
    """

    SOURCE = "kobotoolbox"

    def __init__(
        self,
        raw_submission_repository: (
            RawSubmissionRepository | None
        ) = None,
        program_repository: (
            ProgramRepository | None
        ) = None,
        location_repository: (
            LocationRepository | None
        ) = None,
        field_officer_repository: (
            FieldOfficerRepository | None
        ) = None,
        data_quality_issue_repository: (
            DataQualityIssueRepository | None
        ) = None,
    ) -> None:
        self.raw_submission_repository = (
            raw_submission_repository
            or RawSubmissionRepository()
        )

        self.program_repository = (
            program_repository
            or ProgramRepository()
        )

        self.location_repository = (
            location_repository
            or LocationRepository()
        )

        self.field_officer_repository = (
            field_officer_repository
            or FieldOfficerRepository()
        )

        self.data_quality_issue_repository = (
            data_quality_issue_repository
            or DataQualityIssueRepository()
        )

    def load(
        self,
        *,
        session: Session,
        pipeline_result: PipelineResult,
    ) -> DatabaseLoadResult:
        """
        Persist the complete validation result.

        Accepted and rejected submissions are processed
        independently so that one database failure does not stop
        the remaining records.
        """

        result = DatabaseLoadResult(
            total_records=pipeline_result.total_records,
        )

        for accepted_submission in (
            pipeline_result.accepted_records
        ):
            self._load_accepted_safely(
                session=session,
                accepted_submission=accepted_submission,
                result=result,
            )

        for rejected_submission in (
            pipeline_result.rejected_records
        ):
            self._load_rejected_safely(
                session=session,
                rejected_submission=rejected_submission,
                result=result,
            )

        return result

    def _load_accepted_safely(
        self,
        *,
        session: Session,
        accepted_submission: AcceptedSubmission,
        result: DatabaseLoadResult,
    ) -> None:
        """
        Persist one accepted submission.

        Each record uses its own transaction boundary.
        """

        submission = accepted_submission.submission

        try:
            status = self._load_accepted(
                session=session,
                accepted_submission=accepted_submission,
            )

            if status == "inserted":
                session.commit()

                result.accepted_inserted += 1

            elif status == "skipped":
                session.rollback()

                result.skipped_records += 1

        except IntegrityError as error:
            session.rollback()

            result.failed_records += 1

            result.failures.append(
                LoadFailure(
                    submission_reference=(
                        submission.kobo_uuid
                    ),
                    error=str(error.orig),
                )
            )

        except Exception as error:
            session.rollback()

            result.failed_records += 1

            result.failures.append(
                LoadFailure(
                    submission_reference=(
                        submission.kobo_uuid
                    ),
                    error=str(error),
                )
            )

    def _load_rejected_safely(
        self,
        *,
        session: Session,
        rejected_submission: RejectedSubmission,
        result: DatabaseLoadResult,
    ) -> None:
        """
        Persist one rejected submission and its data quality issue.
        """

        try:
            status = self._load_rejected(
                session=session,
                rejected_submission=rejected_submission,
            )

            if status == "persisted":
                session.commit()

                result.rejected_persisted += 1

            elif status == "skipped":
                session.rollback()

                result.skipped_records += 1

        except IntegrityError as error:
            session.rollback()

            result.failed_records += 1

            result.failures.append(
                LoadFailure(
                    submission_reference=(
                        self._normalize_reference(
                            rejected_submission
                            .submission_reference
                        )
                    ),
                    error=str(error.orig),
                )
            )

        except Exception as error:
            session.rollback()

            result.failed_records += 1

            result.failures.append(
                LoadFailure(
                    submission_reference=(
                        self._normalize_reference(
                            rejected_submission
                            .submission_reference
                        )
                    ),
                    error=str(error),
                )
            )

    def _load_accepted(
        self,
        *,
        session: Session,
        accepted_submission: AcceptedSubmission,
    ) -> str:
        """
        Persist one validated Kobo submission.

        Returns:

            inserted
            skipped
        """

        submission = accepted_submission.submission

        existing_raw_submission = (
            self.raw_submission_repository
            .get_by_source_and_external_id(
                session,
                source=self.SOURCE,
                external_submission_id=(
                    submission.kobo_uuid
                ),
            )
        )

        if existing_raw_submission is not None:
            return "skipped"

        raw_submission = (
            self.raw_submission_repository.create(
                session,
                source=self.SOURCE,
                external_submission_id=(
                    submission.kobo_uuid
                ),
                payload=(
                    accepted_submission
                    .raw_submission
                ),
                retrieved_at=datetime.now(
                    timezone.utc
                ),
                processing_status="processing",
            )
        )

        program = (
            self.program_repository.get_or_create(
                session,
                name=(
                    submission
                    .program_data
                    .program
                ),
            )
        )

        location = (
            self.location_repository.get_or_create(
                session,
                state=(
                    submission
                    .location_data
                    .state
                ),
                lga=(
                    submission
                    .location_data
                    .lga
                ),
                community=(
                    submission
                    .location_data
                    .community
                ),
                latitude=(
                    submission
                    .location_data
                    .gps_location
                    .latitude
                ),
                longitude=(
                    submission
                    .location_data
                    .gps_location
                    .longitude
                ),
            )
        )

        field_officer_external_id = (
            self._resolve_field_officer_external_id(
                submission
            )
        )

        field_officer_name = (
            self._resolve_field_officer_name(
                submission
            )
        )

        field_officer = (
            self.field_officer_repository
            .get_or_create(
                session,
                external_id=(
                    field_officer_external_id
                ),
                full_name=field_officer_name,
            )
        )

        activity = Activity(
            raw_submission_id=raw_submission.id,

            program_id=program.id,

            location_id=location.id,

            field_officer_id=field_officer.id,

            activity_type=(
                submission
                .activity_data
                .activity_type
            ),

            activity_title=(
                submission
                .activity_data
                .activity_title
            ),

            activity_description=(
                submission
                .activity_data
                .activity_description
            ),

            activity_date=(
                submission
                .activity_data
                .activity_date
            ),

            status=(
                submission
                .activity_data
                .activity_status
            ),

            target_participants=(
                submission
                .activity_data
                .target_participants
            ),

            actual_participants=(
                submission
                .participant_data
                .actual_participants
            ),

            male_participants=(
                submission
                .participant_data
                .male_participants
            ),

            female_participants=(
                submission
                .participant_data
                .female_participants
            ),

            youth_participants=(
                submission
                .participant_data
                .youth_participants
            ),

            adult_participants=(
                submission
                .participant_data
                .adult_participants
            ),

            submitted_at=(
                self._resolve_submitted_at(
                    submission
                )
            ),
        )

        session.add(activity)

        raw_submission.processing_status = (
            "processed"
        )

        raw_submission.processed_at = (
            datetime.now(timezone.utc)
        )

        session.flush()

        return "inserted"

    def _load_rejected(
        self,
        *,
        session: Session,
        rejected_submission: RejectedSubmission,
    ) -> str:
        """
        Persist a rejected submission.

        The original payload is retained and the reason for
        rejection is stored as a DataQualityIssue.
        """

        external_submission_id = (
            self._resolve_rejected_external_id(
                rejected_submission
            )
        )

        existing_raw_submission = (
            self.raw_submission_repository
            .get_by_source_and_external_id(
                session,
                source=self.SOURCE,
                external_submission_id=(
                    external_submission_id
                ),
            )
        )

        if existing_raw_submission is not None:
            return "skipped"

        now = datetime.now(timezone.utc)

        raw_submission = (
            self.raw_submission_repository.create(
                session,
                source=self.SOURCE,
                external_submission_id=(
                    external_submission_id
                ),
                payload=(
                    rejected_submission
                    .raw_submission
                ),
                retrieved_at=now,
                processing_status="failed",
            )
        )

        raw_submission.processed_at = now

        self.data_quality_issue_repository.create(
            session,
            raw_submission_id=raw_submission.id,
            rule_name="kobo_submission_validation",
            severity="error",
            issue_description=(
                rejected_submission.error
            ),
            detected_at=now,
            status="open",
        )

        session.flush()

        return "persisted"

    @staticmethod
    def _resolve_submitted_at(
        submission: KoboSubmission,
    ) -> datetime:
        """
        Determine the best available timestamp representing when
        the submission entered the collection system.
        """

        if submission.submission_time is not None:
            return submission.submission_time

        return submission.end_time

    @staticmethod
    def _resolve_field_officer_external_id(
        submission: KoboSubmission,
    ) -> str:
        """
        Resolve the strongest available field officer identifier.

        Priority:

            submitted_by
                ↓
            username
                ↓
            device_id
                ↓
            Kobo submission UUID
        """

        if submission.submitted_by:
            return submission.submitted_by

        if (
            submission.username
            and submission.username.lower()
            != "username not found"
        ):
            return submission.username

        if submission.device_id:
            return submission.device_id

        return (
            f"kobo-submission-"
            f"{submission.kobo_uuid}"
        )

    @staticmethod
    def _resolve_field_officer_name(
        submission: KoboSubmission,
    ) -> str:
        """
        Resolve a display name for the field officer.
        """

        if submission.submitted_by:
            return submission.submitted_by

        if (
            submission.username
            and submission.username.lower()
            != "username not found"
        ):
            return submission.username

        if submission.device_id:
            return (
                f"Field Officer "
                f"({submission.device_id})"
            )

        return "Unknown Field Officer"

    @staticmethod
    def _normalize_reference(
        reference: str | int | None,
    ) -> str | None:
        """
        Convert a submission reference into a database-compatible
        string value.
        """

        if reference is None:
            return None

        return str(reference)

    def _resolve_rejected_external_id(
        self,
        rejected_submission: RejectedSubmission,
    ) -> str:
        """
        Determine a stable external identifier for a rejected
        submission.

        Prefer the submission reference generated during validation.
        If it is unavailable, use the raw Kobo metadata.
        """

        reference = self._normalize_reference(
            rejected_submission.submission_reference
        )

        if reference is not None:
            return reference

        raw_submission = (
            rejected_submission.raw_submission
        )

        raw_uuid = raw_submission.get("_uuid")

        if raw_uuid:
            return str(raw_uuid)

        raw_id = raw_submission.get("_id")

        if raw_id is not None:
            return str(raw_id)

        raise ValueError(
            "Rejected submission does not contain a usable "
            "external identifier."
        )