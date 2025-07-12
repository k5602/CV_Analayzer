"""
KeywordFeedback: Generates keyword match feedback for resume analysis.
Refactored out of FeedbackGenerator for single-responsibility.
"""

from typing import Dict, List, Optional

class KeywordFeedback:
    """
    Provides feedback on keyword matching between resume and job description.
    """

    @staticmethod
    def generate(feedback: Dict, keyword_analysis: Optional[Dict]) -> None:
        """
        Populate the feedback dictionary with keyword match score, matched/missing keywords, and recommendations.

        Args:
            feedback: The feedback dictionary to update.
            keyword_analysis: The keyword analysis results.
        """
        if not keyword_analysis:
            feedback["keyword_match"] = {
                "score": 0,
                "matched_keywords": [],
                "missing_keywords": [],
                "recommendations": ["No job description provided. Keyword matching not performed."]
            }
            return

        score = keyword_analysis.get("overall_match_percentage", 0)
        matched_keywords = keyword_analysis.get("matching_keywords", [])
        missing_keywords = keyword_analysis.get("missing_keywords", [])
        recommendations = []

        # Recommend adding missing keywords
        if missing_keywords:
            recommendations.append(
                f"Consider adding these missing keywords from the job description: {', '.join(missing_keywords[:10])}"
            )

        # Highlight strong matches
        if matched_keywords:
            recommendations.append(
                f"Strong keyword matches: {', '.join(matched_keywords[:10])}"
            )

        feedback["keyword_match"] = {
            "score": score,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "recommendations": recommendations
        }

    @staticmethod
    def summary(keyword_analysis: Optional[Dict]) -> str:
        """
        Generate a summary string for keyword matching.

        Args:
            keyword_analysis: The keyword analysis results.

        Returns:
            Summary string.
        """
        if not keyword_analysis:
            return "No keyword matching performed (no job description provided)."

        score = keyword_analysis.get("overall_match_percentage", 0)
        if score >= 80:
            return "Your resume closely matches the job description keywords. Excellent alignment."
        elif score >= 60:
            return "Your resume matches many job description keywords. Consider adding more for stronger alignment."
        else:
            return "Your resume has low keyword alignment with the job description. Add relevant keywords to improve matching."
