"""
Import all ORM models.

This module exists to ensure every SQLAlchemy model is registered with
Base.metadata before database migrations are generated.
"""

from app.models import (
    Activity,
    DataQualityIssue,
    FieldOfficer,
    Location,
    Program,
    ProgramTarget,
    RawSubmission,
)

__all__ = [
    "Activity",
    "DataQualityIssue",
    "FieldOfficer",
    "Location",
    "Program",
    "ProgramTarget",
    "RawSubmission",
]