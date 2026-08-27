from pydantic import BaseModel


class MonitoringSummary(BaseModel):
    """
    Represents a high-level summary of program monitoring data.

    These metrics provide a quick overview of activities,
    participation, and completion performance.
    """

    total_activities: int

    completed_activities: int

    planned_activities: int

    cancelled_activities: int

    total_target_participants: int

    total_actual_participants: int

    total_male_participants: int

    total_female_participants: int

    total_youth_participants: int

    total_adult_participants: int

    participant_achievement_percentage: float