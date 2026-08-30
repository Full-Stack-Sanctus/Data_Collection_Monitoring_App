from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.schemas.monitoring import (
    DataQualityIssueBreakdown,
    DataQualitySummary,
    GeographicPerformance,
    MonitoringSummary,
    ProgramPerformance,
)
from app.services.monitoring_service import (
    MonitoringService,
)

from app.api.dependencies.auth import (
    require_api_key,
)

from typing import Annotated

from app.schemas.auth import TokenPayload
from app.security.dependencies import (
    get_current_principal,
)


from app.security.authorization import require_role


router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"],
    dependencies=[
        Depends(require_api_key),
        Depends(get_current_principal),
        Depends(require_role(
            "admin",
            "analyst",
            "viewer",
            )
        ),
    ],
)


def get_monitoring_service() -> MonitoringService:
    """
    Provide the monitoring service to API endpoints.

    Keeping service construction behind a dependency makes the API
    layer easier to test and allows the implementation to evolve
    without changing individual endpoints.
    """

    return MonitoringService()


@router.get(
    "/summary",
    response_model=MonitoringSummary,
)
def get_monitoring_summary(
    session: Session = Depends(get_db),
    service: MonitoringService = Depends(
        get_monitoring_service
    ),
) -> MonitoringSummary:
    """
    Return high-level program monitoring indicators.
    """

    return service.get_summary(session=session)


@router.get(
    "/programs",
    response_model=list[ProgramPerformance],
    summary="Get program performance",
    description=(
        "Return activity and participant performance metrics "
        "grouped by program."
    ),
    response_description=(
        "Program-level monitoring performance."
    ),
)
def get_program_performance(
    session: Session = Depends(get_db),
    service: MonitoringService = Depends(
        get_monitoring_service
    ),
) -> list[ProgramPerformance]:
    """
    Return monitoring performance grouped by program.
    """

    return service.get_program_performance(session=session)


@router.get(
    "/geography",
    response_model=list[GeographicPerformance],
    summary="Get geographic performance",
    description=(
        "Return activity and participant performance metrics "
        "grouped by state, LGA, and community."
    ),
    response_description=(
        "Geographic monitoring performance."
    ),
)
def get_geographic_performance(
    session: Session = Depends(get_db),
    service: MonitoringService = Depends(
        get_monitoring_service
    ),
) -> list[GeographicPerformance]:
    """
    Return monitoring performance grouped by geographic location.
    """

    return service.get_geographic_performance(session=session)


@router.get(
    "/data-quality",
    response_model=DataQualitySummary,
    summary="Get program performance",
    description=(
        "Return activity and participant performance metrics "
        "grouped by program."
    ),
    response_description=(
        "Program-level monitoring performance."
    ),
)
def get_data_quality_summary(
    session: Session = Depends(get_db),
    service: MonitoringService = Depends(
        get_monitoring_service
    ),
) -> DataQualitySummary:
    """
    Return high-level data quality and processing indicators.
    """

    return service.get_data_quality_summary(session=session)


@router.get(
    "/data-quality/issues",
    response_model=list[DataQualityIssueBreakdown],
    summary="Get data quality issue breakdown",
    description=(
        "Return data quality issues grouped by validation "
        "rule and severity."
    ),
    response_description=(
        "Data quality issue counts by rule and severity."
    ),
)
def get_data_quality_issue_breakdown(
    session: Session = Depends(get_db),
    service: MonitoringService = Depends(
        get_monitoring_service
    ),
) -> list[DataQualityIssueBreakdown]:
    """
    Return data quality issues grouped by validation rule
    and severity.
    """

    return service.get_data_quality_issue_breakdown(session=session)