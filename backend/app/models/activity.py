from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.field_officer import FieldOfficer
    from app.models.location import Location
    from app.models.program import Program
    from app.models.raw_submission import RawSubmission


class Activity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents a normalized program activity collected from the field.
    """

    __tablename__ = "activities"

    __table_args__ = (
        CheckConstraint(
            "target_participants >= 0",
            name="ck_activities_non_negative_target_participants",
        ),
        CheckConstraint(
            "actual_participants >= 0",
            name="ck_activities_non_negative_actual_participants",
        ),
        CheckConstraint(
            "male_participants >= 0",
            name="ck_activities_non_negative_male_participants",
        ),
        CheckConstraint(
            "female_participants >= 0",
            name="ck_activities_non_negative_female_participants",
        ),
        CheckConstraint(
            "youth_participants >= 0",
            name="ck_activities_non_negative_youth_participants",
        ),
        CheckConstraint(
            "adult_participants >= 0",
            name="ck_activities_non_negative_adult_participants",
        ),
        CheckConstraint(
            "male_participants + female_participants = actual_participants",
            name="ck_activities_gender_total_matches_actual",
        ),
        CheckConstraint(
            "youth_participants + adult_participants = actual_participants",
            name="ck_activities_age_total_matches_actual",
        ),
        Index(
            "ix_activities_program_activity_date",
            "program_id",
            "activity_date",
        ),
        Index(
            "ix_activities_location_activity_date",
            "location_id",
            "activity_date",
        ),
        Index(
            "ix_activities_status_activity_date",
            "status",
            "activity_date",
        ),
    )

    raw_submission_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "raw_submissions.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        unique=True,
    )

    program_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "programs.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    location_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "locations.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    field_officer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "field_officers.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    activity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    activity_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    activity_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    activity_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="completed",
        server_default="completed",
        index=True,
    )

    target_participants: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    actual_participants: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    male_participants: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    female_participants: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    youth_participants: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    adult_participants: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    raw_submission: Mapped[RawSubmission] = relationship(
        back_populates="activity",
    )

    program: Mapped[Program] = relationship(
        back_populates="activities",
    )

    location: Mapped[Location] = relationship(
        back_populates="activities",
    )

    field_officer: Mapped[FieldOfficer] = relationship(
        back_populates="activities",
    )