from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.program_target import ProgramTarget


class Program(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents a program or intervention being monitored.
    """

    __tablename__ = "programs"

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    activities: Mapped[list[Activity]] = relationship(
        back_populates="program",
    )

    targets: Mapped[list[ProgramTarget]] = relationship(
        back_populates="program",
    )