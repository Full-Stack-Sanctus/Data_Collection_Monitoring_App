from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.activity import Activity


class MonitoringRepository:
    """
    Provides database aggregation queries for program monitoring.

    This repository is responsible only for retrieving aggregated
    monitoring data from the normalized Activity records.
    """

    def get_summary(
        self,
        session: Session,
    ) -> dict[str, int]:
        """
        Retrieve the aggregated values required to build the
        high-level monitoring summary.

        The repository returns raw aggregate values. Percentage
        calculations and other business logic belong in the
        monitoring service layer.
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

        row = session.execute(
            statement
        ).mappings().one()

        return {
            "total_activities": int(
                row["total_activities"]
            ),

            "completed_activities": int(
                row["completed_activities"]
            ),

            "cancelled_activities": int(
                row["cancelled_activities"]
            ),

            "total_target_participants": int(
                row["total_target_participants"]
            ),

            "total_actual_participants": int(
                row["total_actual_participants"]
            ),

            "total_male_participants": int(
                row["total_male_participants"]
            ),

            "total_female_participants": int(
                row["total_female_participants"]
            ),

            "total_youth_participants": int(
                row["total_youth_participants"]
            ),

            "total_adult_participants": int(
                row["total_adult_participants"]
            ),
        }