from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.data_quality_issue import (
    DataQualityIssue,
)
from app.models.location import Location
from app.models.program import Program
from app.models.raw_submission import (
    RawSubmission,
)


class MonitoringRepository:
    """
    Provides aggregated monitoring data from activity records.

    This repository is responsible only for database queries and
    aggregation. Business calculations are handled by the monitoring
    service layer.
    """

    def get_summary_totals(
        self,
        session: Session,
    ) -> dict[str, int]:
        """
        Retrieve high-level activity and participant totals.

        The aggregation is performed directly by PostgreSQL so that
        the application does not need to load every Activity record
        into memory before calculating monitoring totals.
        """

        statement = select(
            func.count(
                Activity.id
            ).label(
                "total_activities"
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            Activity.status == "completed",
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label(
                "completed_activities"
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            Activity.status == "cancelled",
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label(
                "cancelled_activities"
            ),
            func.coalesce(
                func.sum(
                    Activity.target_participants
                ),
                0,
            ).label(
                "total_target_participants"
            ),
            func.coalesce(
                func.sum(
                    Activity.actual_participants
                ),
                0,
            ).label(
                "total_actual_participants"
            ),
            func.coalesce(
                func.sum(
                    Activity.male_participants
                ),
                0,
            ).label(
                "total_male_participants"
            ),
            func.coalesce(
                func.sum(
                    Activity.female_participants
                ),
                0,
            ).label(
                "total_female_participants"
            ),
            func.coalesce(
                func.sum(
                    Activity.youth_participants
                ),
                0,
            ).label(
                "total_youth_participants"
            ),
            func.coalesce(
                func.sum(
                    Activity.adult_participants
                ),
                0,
            ).label(
                "total_adult_participants"
            ),
        )

        result = (
            session.execute(
                statement
            )
            .mappings()
            .one()
        )

        return {
            "total_activities": (
                result["total_activities"]
            ),
            "completed_activities": (
                result["completed_activities"]
            ),
            "cancelled_activities": (
                result["cancelled_activities"]
            ),
            "total_target_participants": (
                result["total_target_participants"]
            ),
            "total_actual_participants": (
                result["total_actual_participants"]
            ),
            "total_male_participants": (
                result["total_male_participants"]
            ),
            "total_female_participants": (
                result["total_female_participants"]
            ),
            "total_youth_participants": (
                result["total_youth_participants"]
            ),
            "total_adult_participants": (
                result["total_adult_participants"]
            ),
        }

    def get_program_performance(
        self,
        session: Session,
    ) -> list[dict[str, object]]:
        """
        Retrieve aggregated monitoring metrics for every program.

        Each result contains activity counts and participant totals
        calculated from the activities associated with the program.
        """

        statement = (
            select(
                Program.id.label(
                    "program_id"
                ),
                Program.name.label(
                    "program_name"
                ),
                func.count(
                    Activity.id
                ).label(
                    "total_activities"
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                Activity.status
                                == "completed",
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label(
                    "completed_activities"
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                Activity.status
                                == "cancelled",
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label(
                    "cancelled_activities"
                ),
                func.coalesce(
                    func.sum(
                        Activity.target_participants
                    ),
                    0,
                ).label(
                    "total_target_participants"
                ),
                func.coalesce(
                    func.sum(
                        Activity.actual_participants
                    ),
                    0,
                ).label(
                    "total_actual_participants"
                ),
            )
            .outerjoin(
                Activity,
                Activity.program_id == Program.id,
            )
            .group_by(
                Program.id,
                Program.name,
            )
            .order_by(
                Program.name,
            )
        )

        rows = (
            session.execute(
                statement
            )
            .mappings()
        )

        return [
            dict(row)
            for row in rows
        ]

    def get_geographic_performance(
        self,
        session: Session,
    ) -> list[dict[str, object]]:
        """
        Calculate activity and participant performance grouped by
        geographic location.

        Results are grouped by state, LGA, and community.
        """

        statement = (
            select(
                Location.state.label(
                    "state"
                ),
                Location.lga.label(
                    "lga"
                ),
                Location.community.label(
                    "community"
                ),
                func.count(
                    Activity.id
                ).label(
                    "total_activities"
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                Activity.status
                                == "completed",
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label(
                    "completed_activities"
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                Activity.status
                                == "cancelled",
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label(
                    "cancelled_activities"
                ),
                func.coalesce(
                    func.sum(
                        Activity.target_participants
                    ),
                    0,
                ).label(
                    "total_target_participants"
                ),
                func.coalesce(
                    func.sum(
                        Activity.actual_participants
                    ),
                    0,
                ).label(
                    "total_actual_participants"
                ),
            )
            .join(
                Location,
                Activity.location_id == Location.id,
            )
            .group_by(
                Location.state,
                Location.lga,
                Location.community,
            )
            .order_by(
                Location.state,
                Location.lga,
                Location.community,
            )
        )

        results = (
            session.execute(
                statement
            )
            .mappings()
        )

        return [
            dict(row)
            for row in results
        ]

    def get_data_quality_summary(
        self,
        session: Session,
    ) -> dict[str, object]:
        """
        Retrieve aggregate submission processing and data quality
        metrics from the database.
        """

        submission_statement = select(
            func.count(
                RawSubmission.id
            ).label(
                "total_submissions"
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            RawSubmission.processing_status
                            == "processed",
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label(
                "processed_submissions"
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            RawSubmission.processing_status
                            == "failed",
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label(
                "failed_submissions"
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            RawSubmission.processing_status
                            == "pending",
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label(
                "pending_submissions"
            ),
        )

        submission_result = (
            session.execute(
                submission_statement
            )
            .mappings()
            .one()
        )

        issue_statement = select(
            func.count(
                DataQualityIssue.id
            ).label(
                "total_quality_issues"
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            DataQualityIssue.status
                            == "open",
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label(
                "open_quality_issues"
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            DataQualityIssue.status
                            == "resolved",
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label(
                "resolved_quality_issues"
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            DataQualityIssue.severity
                            == "error",
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label(
                "error_quality_issues"
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            DataQualityIssue.severity
                            == "warning",
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label(
                "warning_quality_issues"
            ),
        )

        issue_result = (
            session.execute(
                issue_statement
            )
            .mappings()
            .one()
        )

        return {
            **dict(submission_result),
            **dict(issue_result),
        }

    def get_data_quality_issue_breakdown(
        self,
        session: Session,
    ) -> list[dict[str, object]]:
        """
        Retrieve data quality issues grouped by validation rule
        and severity.
        """

        statement = (
            select(
                DataQualityIssue.rule_name.label(
                    "rule_name"
                ),
                DataQualityIssue.severity.label(
                    "severity"
                ),
                func.count(
                    DataQualityIssue.id
                ).label(
                    "issue_count"
                ),
            )
            .group_by(
                DataQualityIssue.rule_name,
                DataQualityIssue.severity,
            )
            .order_by(
                DataQualityIssue.rule_name,
                DataQualityIssue.severity,
            )
        )

        results = (
            session.execute(
                statement
            )
            .mappings()
        )

        return [
            dict(row)
            for row in results
        ]