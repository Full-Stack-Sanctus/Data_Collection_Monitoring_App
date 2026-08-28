from sqlalchemy.orm import Session

from app.repositories.monitoring_repository import (
    MonitoringRepository,
)
from app.schemas.monitoring import (
    DataQualityIssueBreakdown,
    DataQualitySummary,
    GeographicPerformance,
    MonitoringSummary,
    ProgramPerformance,
)


class MonitoringService:
    """
    Provides monitoring indicators calculated from normalized
    program activity data.

    The repository is responsible for retrieving aggregated database
    values, while this service applies monitoring business logic and
    returns structured monitoring results.
    """

    def __init__(
        self,
        monitoring_repository: (
            MonitoringRepository | None
        ) = None,
    ) -> None:
        self.monitoring_repository = (
            monitoring_repository
            or MonitoringRepository()
        )

    def get_summary(
        self,
        *,
        session: Session,
    ) -> MonitoringSummary:
        """
        Retrieve the overall monitoring summary.

        The participant achievement percentage is calculated from
        the aggregated actual and target participant totals.

        A target value of zero produces an achievement percentage
        of 0.0 to prevent division by zero.
        """

        totals = (
            self.monitoring_repository
            .get_summary_totals(
                session
            )
        )

        total_target_participants = (
            totals["total_target_participants"]
        )

        total_actual_participants = (
            totals["total_actual_participants"]
        )

        participant_achievement_percentage = (
            self._calculate_percentage(
                numerator=total_actual_participants,
                denominator=total_target_participants,
            )
        )

        return MonitoringSummary(
            total_activities=(
                totals["total_activities"]
            ),
            completed_activities=(
                totals["completed_activities"]
            ),
            cancelled_activities=(
                totals["cancelled_activities"]
            ),
            total_target_participants=(
                total_target_participants
            ),
            total_actual_participants=(
                total_actual_participants
            ),
            total_male_participants=(
                totals["total_male_participants"]
            ),
            total_female_participants=(
                totals["total_female_participants"]
            ),
            total_youth_participants=(
                totals["total_youth_participants"]
            ),
            total_adult_participants=(
                totals["total_adult_participants"]
            ),
            participant_achievement_percentage=(
                participant_achievement_percentage
            ),
        )

    def get_program_performance(
        self,
        *,
        session: Session,
    ) -> list[ProgramPerformance]:
        """
        Retrieve monitoring performance metrics grouped by program.

        The repository performs the database aggregation while this
        service calculates derived monitoring indicators.
        """

        program_metrics = (
            self.monitoring_repository
            .get_program_performance(
                session
            )
        )

        results: list[ProgramPerformance] = []

        for metrics in program_metrics:
            target_participants = int(
                metrics[
                    "total_target_participants"
                ]
            )

            actual_participants = int(
                metrics[
                    "total_actual_participants"
                ]
            )

            achievement_percentage = (
                self._calculate_percentage(
                    numerator=actual_participants,
                    denominator=target_participants,
                )
            )

            results.append(
                ProgramPerformance(
                    program_id=str(
                        metrics["program_id"]
                    ),
                    program_name=str(
                        metrics["program_name"]
                    ),
                    total_activities=int(
                        metrics["total_activities"]
                    ),
                    completed_activities=int(
                        metrics[
                            "completed_activities"
                        ]
                    ),
                    cancelled_activities=int(
                        metrics[
                            "cancelled_activities"
                        ]
                    ),
                    total_target_participants=(
                        target_participants
                    ),
                    total_actual_participants=(
                        actual_participants
                    ),
                    participant_achievement_percentage=(
                        achievement_percentage
                    ),
                )
            )

        return results

    def get_geographic_performance(
        self,
        *,
        session: Session,
    ) -> list[GeographicPerformance]:
        """
        Calculate monitoring performance for every geographic
        location represented in the database.

        Achievement percentage is calculated from aggregated
        participant totals.
        """

        geographic_records = (
            self.monitoring_repository
            .get_geographic_performance(
                session
            )
        )

        performances: list[
            GeographicPerformance
        ] = []

        for record in geographic_records:
            target_participants = int(
                record[
                    "total_target_participants"
                ]
            )

            actual_participants = int(
                record[
                    "total_actual_participants"
                ]
            )

            achievement_percentage = (
                self._calculate_percentage(
                    numerator=actual_participants,
                    denominator=target_participants,
                )
            )

            performances.append(
                GeographicPerformance(
                    state=str(
                        record["state"]
                    ),
                    lga=str(
                        record["lga"]
                    ),
                    community=str(
                        record["community"]
                    ),
                    total_activities=int(
                        record[
                            "total_activities"
                        ]
                    ),
                    completed_activities=int(
                        record[
                            "completed_activities"
                        ]
                    ),
                    cancelled_activities=int(
                        record[
                            "cancelled_activities"
                        ]
                    ),
                    total_target_participants=(
                        target_participants
                    ),
                    total_actual_participants=(
                        actual_participants
                    ),
                    participant_achievement_percentage=(
                        achievement_percentage
                    ),
                )
            )

        return performances

    def get_data_quality_summary(
        self,
        *,
        session: Session,
    ) -> DataQualitySummary:
        """
        Calculate high-level data quality and submission
        processing indicators.
        """

        metrics = (
            self.monitoring_repository
            .get_data_quality_summary(
                session
            )
        )

        processing_success_percentage = (
            self._calculate_percentage(
                numerator=(
                    metrics[
                        "processed_submissions"
                    ]
                ),
                denominator=(
                    metrics[
                        "total_submissions"
                    ]
                ),
            )
        )

        return DataQualitySummary(
            total_submissions=(
                metrics[
                    "total_submissions"
                ]
            ),
            processed_submissions=(
                metrics[
                    "processed_submissions"
                ]
            ),
            failed_submissions=(
                metrics[
                    "failed_submissions"
                ]
            ),
            pending_submissions=(
                metrics[
                    "pending_submissions"
                ]
            ),
            processing_success_percentage=(
                processing_success_percentage
            ),
            total_quality_issues=(
                metrics[
                    "total_quality_issues"
                ]
            ),
            open_quality_issues=(
                metrics[
                    "open_quality_issues"
                ]
            ),
            resolved_quality_issues=(
                metrics[
                    "resolved_quality_issues"
                ]
            ),
            error_quality_issues=(
                metrics[
                    "error_quality_issues"
                ]
            ),
            warning_quality_issues=(
                metrics[
                    "warning_quality_issues"
                ]
            ),
        )

    def get_data_quality_issue_breakdown(
        self,
        *,
        session: Session,
    ) -> list[DataQualityIssueBreakdown]:
        """
        Return data quality issues grouped by validation rule
        and severity.
        """

        records = (
            self.monitoring_repository
            .get_data_quality_issue_breakdown(
                session
            )
        )

        return [
            DataQualityIssueBreakdown(
                rule_name=record[
                    "rule_name"
                ],
                severity=record[
                    "severity"
                ],
                issue_count=int(
                    record[
                        "issue_count"
                    ]
                ),
            )
            for record in records
        ]

    @staticmethod
    def _calculate_percentage(
        *,
        numerator: int,
        denominator: int,
    ) -> float:
        """
        Calculate a percentage while safely handling a zero
        denominator.

        The result is rounded to two decimal places for consistent
        reporting and API consumption.
        """

        if denominator == 0:
            return 0.0

        return round(
            (numerator / denominator) * 100,
            2,
        )