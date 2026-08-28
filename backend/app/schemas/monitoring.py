from pydantic import BaseModel


class MonitoringSummary(BaseModel):
    """
    Represents a high-level summary of program monitoring data.

    These metrics provide a quick overview of activities,
    participation, and completion performance.
    """

    total_activities: int

    completed_activities: int

    cancelled_activities: int

    total_target_participants: int

    total_actual_participants: int

    total_male_participants: int

    total_female_participants: int

    total_youth_participants: int

    total_adult_participants: int

    participant_achievement_percentage: float


class MonitoringSummary(BaseModel):
    """
    Represents a high-level summary of program monitoring data.

    These metrics provide a quick overview of activities,
    participation, and completion performance.
    """

    total_activities: int

    completed_activities: int

    cancelled_activities: int

    total_target_participants: int

    total_actual_participants: int

    total_male_participants: int

    total_female_participants: int

    total_youth_participants: int

    total_adult_participants: int

    participant_achievement_percentage: float


class ProgramPerformance(BaseModel):
    """
    Represents monitoring performance metrics for a single program.
    """

    program_id: str

    program_name: str

    total_activities: int

    completed_activities: int

    cancelled_activities: int

    total_target_participants: int

    total_actual_participants: int

    participant_achievement_percentage: float
    

class GeographicPerformance(BaseModel):
    """
    Represents monitoring performance metrics for a geographic
    location.

    The same schema can represent performance at the state,
    LGA, or community level.
    """

    state: str

    lga: str

    community: str

    total_activities: int

    completed_activities: int

    cancelled_activities: int

    total_target_participants: int

    total_actual_participants: int

    participant_achievement_percentage: float
    
    
class DataQualitySummary(BaseModel):
    """
    Represents a high-level summary of data quality and
    submission processing performance.
    """

    total_submissions: int

    processed_submissions: int

    failed_submissions: int

    pending_submissions: int

    processing_success_percentage: float

    total_quality_issues: int

    open_quality_issues: int

    resolved_quality_issues: int

    error_quality_issues: int

    warning_quality_issues: int
    

class DataQualityIssueBreakdown(BaseModel):
    """
    Represents a breakdown of data quality issues by validation
    rule and severity.
    """

    rule_name: str

    severity: str

    issue_count: int