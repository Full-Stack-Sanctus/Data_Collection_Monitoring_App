from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.data_quality_issue import DataQualityIssue


class RawSubmission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Stores the original submission received from an external collection
    platform before transformation into normalized application records.
    """

    __tablename__ = "raw_submissions"

    __table_args__ = (
        Index(
            "ix_raw_submissions_source_external_id",
            "source",
            "external_submission_id",
        ),
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    external_submission_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    processing_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )

    activity: Mapped[Activity | None] = relationship(
        back_populates="raw_submission",
        uselist=False,
    )

    data_quality_issues: Mapped[list[DataQualityIssue]] = relationship(
        back_populates="raw_submission",
    )