"""
ATSFeedback: Generates ATS compatibility feedback for resume analysis.
Only key logic is commented for clarity.
"""

from typing import Dict, List

class ATSFeedback:
    """
    Generates ATS compatibility feedback and summary for the UI.
    """

    @staticmethod
    def generate(feedback: Dict, ats_analysis: Dict) -> None:
        """
        Adds ATS compatibility issues and recommendations to feedback.
        """
        issues = []
        recommendations = []

        score = ats_analysis.get("compatibility_score", 0)
        formatting_issues = ats_analysis.get("formatting_issues", [])
        structure_feedback = ats_analysis.get("structure_feedback", [])
        improvement_suggestions = ats_analysis.get("improvement_suggestions", [])

        # Formatting issues and suggestions
        if formatting_issues:
            issues.extend(formatting_issues)
            recommendations.extend([f"Fix formatting: {issue}" for issue in formatting_issues])

        # Structure feedback and suggestions
        if structure_feedback:
            issues.extend(structure_feedback)
            recommendations.extend([f"Improve structure: {fb}" for fb in structure_feedback])

        # General improvement suggestions
        if improvement_suggestions:
            recommendations.extend(improvement_suggestions)

        feedback["ats_compatibility"] = {
            "score": score,
            "issues": issues,
            "recommendations": recommendations
        }

    @staticmethod
    def summary(ats_analysis: Dict) -> str:
        """
        Returns a human-readable summary for ATS compatibility.
        """
        score = ats_analysis.get("compatibility_score", 0)
        platform = ats_analysis.get("ats_platform", "ATS")
        if score >= 80:
            return f"Your resume is highly compatible with {platform} ATS. Minor improvements may further optimize parsing."
        elif score >= 60:
            return f"Your resume is moderately compatible with {platform} ATS. Address highlighted issues for better results."
        else:
            return f"Your resume has significant ATS compatibility issues for {platform}. Review recommendations to improve parsing and scoring."
