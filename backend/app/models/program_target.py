from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.program import Program


class ProgramTarget(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Defines an expected target for a program indicator within a specific
    reporting period.
    """

    __tablename__ = "program_targets"

    __table_args__ = (
        CheckConstraint(
            "target_value >= 0",
            name="ck_program_targets_non_negative_target",
        ),
        CheckConstraint(
            "period_end >= period_start",
            name="ck_program_targets_valid_period",
        ),
        UniqueConstraint(
            "program_id",
            "indicator_name",
            "period_start",
            "period_end",
            name="uq_program_target_indicator_period",
        ),
        Index(
            "ix_program_targets_program_period",
            "program_id",
            "period_start",
            "period_end",
        ),
    )

    program_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "programs.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    indicator_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    target_value: Mapped[float] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    period_start: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    period_end: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    program: Mapped[Program] = relationship(
        back_populates="targets",
    )