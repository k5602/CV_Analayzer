"""
ATSFeedback: Generates ATS compatibility feedback for resume analysis.
Refactored out of FeedbackGenerator for single-responsibility.
"""

from typing import Dict, List

class ATSFeedback:
    """
    Provides feedback on ATS compatibility based on analysis results.
    """

    @staticmethod
    def generate(feedback: Dict, ats_analysis: Dict) -> None:
        """
        Populate the feedback dictionary with ATS compatibility issues and recommendations.

        Args:
            feedback: The feedback dictionary to update.
            ats_analysis: The ATS analysis results.
        """
        issues = []
        recommendations = []

        # Score and issues
        score = ats_analysis.get("compatibility_score", 0)
        formatting_issues = ats_analysis.get("formatting_issues", [])
        structure_feedback = ats_analysis.get("structure_feedback", [])
        improvement_suggestions = ats_analysis.get("improvement_suggestions", [])

        # Add formatting issues
        if formatting_issues:
            issues.extend(formatting_issues)
            recommendations.extend([f"Fix formatting: {issue}" for issue in formatting_issues])

        # Add structure feedback
        if structure_feedback:
            issues.extend(structure_feedback)
            recommendations.extend([f"Improve structure: {fb}" for fb in structure_feedback])

        # Add improvement suggestions
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
        Generate a summary string for ATS compatibility.

        Args:
            ats_analysis: The ATS analysis results.

        Returns:
            Summary string.
        """
        score = ats_analysis.get("compatibility_score", 0)
        platform = ats_analysis.get("ats_platform", "ATS")
        if score >= 80:
            return f"Your resume is highly compatible with {platform} ATS. Minor improvements may further optimize parsing."
        elif score >= 60:
            return f"Your resume is moderately compatible with {platform} ATS. Address highlighted issues for better results."
        else:
            return f"Your resume has significant ATS compatibility issues for {platform}. Review recommendations to improve parsing and scoring."
