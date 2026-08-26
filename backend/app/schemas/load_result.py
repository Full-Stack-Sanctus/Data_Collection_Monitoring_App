from pydantic import BaseModel, Field


class LoadFailure(BaseModel):
    """
    Represents an unexpected failure that occurred while
    persisting a submission to the database.
    """

    submission_reference: str | None = None

    error: str


class DatabaseLoadResult(BaseModel):
    """
    Summary of a complete database loading operation.

    Accepted records are normalized into Activity records.

    Rejected records are preserved as RawSubmission records and
    linked to DataQualityIssue records.
    """

    total_records: int = Field(
        ge=0,
    )

    accepted_inserted: int = Field(
        default=0,
        ge=0,
    )

    rejected_persisted: int = Field(
        default=0,
        ge=0,
    )

    skipped_records: int = Field(
        default=0,
        ge=0,
    )

    failed_records: int = Field(
        default=0,
        ge=0,
    )

    failures: list[LoadFailure] = Field(
        default_factory=list,
    )