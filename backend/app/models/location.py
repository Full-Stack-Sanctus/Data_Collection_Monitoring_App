from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.activity import Activity


class Location(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Represents the geographic location where an activity occurred.
    """

    __tablename__ = "locations"

    __table_args__ = (
        CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
            name="ck_locations_valid_latitude",
        ),
        CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="ck_locations_valid_longitude",
        ),
        Index(
            "ix_locations_state_lga_community",
            "state",
            "lga",
            "community",
        ),
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    lga: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    community: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    activities: Mapped[list[Activity]] = relationship(
        back_populates="location",
    )