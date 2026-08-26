from typing import Any

from app.schemas.pipeline import PipelineResult


class DataQualityReporter:
    """
    Produces a structured summary of a pipeline run.
    """

    def build_report(
        self,
        result: PipelineResult,
    ) -> dict[str, Any]:
        """
        Generate a serializable quality report.
        """

        return {
            "started_at": result.started_at.isoformat(),
            "completed_at": (
                result.completed_at.isoformat()
                if result.completed_at
                else None
            ),
            "total_records": result.total_records,
            "accepted_records": result.accepted_count,
            "rejected_records": result.rejected_count,
            "acceptance_rate": (
                (
                    result.accepted_count
                    / result.total_records
                    * 100
                )
                if result.total_records > 0
                else 0
            ),
            "rejections": [
                {
                    "submission_reference": (
                        rejected.submission_reference
                    ),
                    "error": rejected.error,
                }
                for rejected in result.rejected_records
            ],
        }