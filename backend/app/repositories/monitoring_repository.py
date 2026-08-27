from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.activity import Activity


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
            func.count(Activity.id).label(
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

        result = session.execute(
            statement
        ).mappings().one()

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