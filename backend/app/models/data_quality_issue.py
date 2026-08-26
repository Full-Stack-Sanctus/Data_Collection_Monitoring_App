from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.raw_submission import RawSubmission


class DataQualityIssue(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents a data quality issue detected during validation or
    transformation of a submitted record.
    """

    __tablename__ = "data_quality_issues"

    __table_args__ = (
        Index(
            "ix_data_quality_issues_status_severity",
            "status",
            "severity",
        ),
        Index(
            "ix_data_quality_issues_raw_submission",
            "raw_submission_id",
        ),
    )

    raw_submission_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "raw_submissions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    rule_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="warning",
        server_default="warning",
    )

    issue_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="open",
        server_default="open",
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    raw_submission: Mapped[RawSubmission] = relationship(
        back_populates="data_quality_issues",
    )