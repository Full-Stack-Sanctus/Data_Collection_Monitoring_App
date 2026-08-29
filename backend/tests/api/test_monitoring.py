# Fixed version of tests/api/test_monitoring.py
from unittest.mock import Mock, ANY
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.monitoring import get_monitoring_service
from app.schemas.monitoring import (
    DataQualityIssueBreakdown,
    DataQualitySummary,
    GeographicPerformance,
    MonitoringSummary,
    ProgramPerformance,
)


def test_monitoring_summary_endpoint(client: TestClient) -> None:
    """
    Verify that the monitoring summary endpoint returns the
    MonitoringSummary response contract.
    """
    summary = MonitoringSummary(
        total_activities=10,
        completed_activities=8,
        planned_activities=1,
        cancelled_activities=1,
        total_target_participants=1000,
        total_actual_participants=850,
        total_male_participants=450,
        total_female_participants=400,
        total_youth_participants=700,
        total_adult_participants=150,
        participant_achievement_percentage=85.0,
    )

    service = Mock()
    service.get_summary.return_value = summary

    app.dependency_overrides[get_monitoring_service] = lambda: service

    try:
        response = client.get("/api/v1/monitoring/summary")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == summary.model_dump()
    # Fixed: Uses ANY to allow the actual injected Session object to pass
    service.get_summary.assert_called_once_with(session=ANY)


def test_program_performance_endpoint(client: TestClient) -> None:
    """
    Verify that program performance is exposed through the
    expected API response contract, aligning with service layer keys.
    """
    expected = [
        ProgramPerformance(
            program_id="digital_skills",
            program_name="digital_skills",
            total_activities=5,
            completed_activities=4,
            cancelled_activities=0,
            total_target_participants=500,
            total_actual_participants=450,
            participant_achievement_percentage=90.0,
        )
    ]

    service = Mock()
    service.get_program_performance.return_value = expected

    app.dependency_overrides[get_monitoring_service] = lambda: service

    try:
        response = client.get("/api/v1/monitoring/programs")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [item.model_dump() for item in expected]
    # Fixed: Uses ANY to allow the actual injected Session object to pass
    service.get_program_performance.assert_called_once_with(session=ANY)


def test_geographic_performance_endpoint(client: TestClient) -> None:
    """
    Verify that geographic performance is exposed through the
    expected API response contract, aligning with service layer keys.
    """
    expected = [
        GeographicPerformance(
            state="rivers",
            lga="Port Harcourt",
            community="Orogbum",
            total_activities=3,
            completed_activities=3,
            cancelled_activities=0,
            total_target_participants=300,
            total_actual_participants=270,
            participant_achievement_percentage=90.0,
        )
    ]

    service = Mock()
    service.get_geographic_performance.return_value = expected

    app.dependency_overrides[get_monitoring_service] = lambda: service

    try:
        response = client.get("/api/v1/monitoring/geography")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [item.model_dump() for item in expected]
    # Fixed: Uses ANY to allow the actual injected Session object to pass
    service.get_geographic_performance.assert_called_once_with(session=ANY)


def test_data_quality_summary_endpoint(client: TestClient) -> None:
    """
    Verify that the data quality summary endpoint returns the
    expected response contract, aligning with service layer properties.
    """
    expected = DataQualitySummary(
        total_submissions=100,
        processed_submissions=90,
        pending_submissions=0,
        failed_submissions=10,
        processing_success_percentage=90.0,
        total_quality_issues=0,
        open_quality_issues=0,
        resolved_quality_issues=0,
        error_quality_issues=0,
        warning_quality_issues=0,
    )

    service = Mock()
    service.get_data_quality_summary.return_value = expected

    app.dependency_overrides[get_monitoring_service] = lambda: service

    try:
        response = client.get("/api/v1/monitoring/data-quality")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == expected.model_dump()
    # Fixed: Uses ANY to allow the actual injected Session object to pass
    service.get_data_quality_summary.assert_called_once_with(session=ANY)


def test_data_quality_issue_breakdown_endpoint(client: TestClient) -> None:
    """
    Verify that data quality issues are exposed using the expected
    response schema.
    """
    expected = [
        DataQualityIssueBreakdown(
            rule_name="participant_gender_total",
            severity="error",
            issue_count=5,
        )
    ]

    service = Mock()
    service.get_data_quality_issue_breakdown.return_value = expected

    app.dependency_overrides[get_monitoring_service] = lambda: service

    try:
        response = client.get("/api/v1/monitoring/data-quality/issues")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [item.model_dump() for item in expected]
    # Fixed: Uses ANY to allow the actual injected Session object to pass
    service.get_data_quality_issue_breakdown.assert_called_once_with(session=ANY)


def test_unknown_monitoring_endpoint_returns_404(client: TestClient) -> None:
    """
    Verify that unknown monitoring resources return HTTP 404.
    """
    response = client.get("/api/v1/monitoring/does-not-exist")
    assert response.status_code == 404
