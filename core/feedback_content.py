"""
ContentFeedback: Generates strengths, weaknesses, and actionable recommendations for resume content.
Only key logic is commented for clarity.
"""

from typing import Dict, List, Any

class ContentFeedback:
    """
    Generates feedback on resume content quality for the user.
    """

    @staticmethod
    def generate(feedback: Dict[str, Any], resume_data: Dict[str, Any]) -> None:
        """
        Analyze resume content and update feedback dict with strengths, weaknesses, and recommendations.
        """
        strengths = []
        weaknesses = []
        recommendations = []

        # Section presence is a strength
        if resume_data.get("summary"):
            strengths.append("Includes a professional summary/objective.")
        if resume_data.get("experience") and len(resume_data["experience"]) > 0:
            strengths.append("Work experience section is present.")
        if resume_data.get("education") and len(resume_data["education"]) > 0:
            strengths.append("Education section is present.")
        if resume_data.get("skills") and len(resume_data["skills"]) > 0:
            strengths.append("Skills section is present.")
        if resume_data.get("projects") and len(resume_data["projects"]) > 0:
            strengths.append("Projects section is present.")

        # Missing sections are flagged as weaknesses
        if not resume_data.get("summary"):
            weaknesses.append("Missing professional summary/objective.")
            recommendations.append("Add a concise summary or objective at the top of your resume.")
        if not resume_data.get("experience") or len(resume_data["experience"]) == 0:
            weaknesses.append("Missing work experience section.")
            recommendations.append("Include relevant work experience with clear job titles and responsibilities.")
        if not resume_data.get("education") or len(resume_data["education"]) == 0:
            weaknesses.append("Missing education section.")
            recommendations.append("Add your educational background, including degrees and institutions.")
        if not resume_data.get("skills") or len(resume_data["skills"]) == 0:
            weaknesses.append("Missing skills section.")
            recommendations.append("List relevant technical and soft skills.")
        if not resume_data.get("projects") or len(resume_data["projects"]) == 0:
            weaknesses.append("Missing projects section.")
            recommendations.append("Include notable projects to showcase your experience and achievements.")

        # Heuristic for resume length
        if resume_data.get("full_text"):
            text = resume_data["full_text"]
            if len(text) < 500:
                weaknesses.append("Resume content is too brief.")
                recommendations.append("Expand your resume to provide more detail on your experience and skills.")
            elif len(text) > 5000:
                weaknesses.append("Resume content is excessively long.")
                recommendations.append("Condense your resume to focus on the most relevant information.")

        feedback["content_quality"] = {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations
        }

    @staticmethod
    def summary(resume_data: Dict[str, Any]) -> str:
        """
        Summarize content quality for the user.
        """
        sections = [
            ("summary", "Summary"),
            ("experience", "Experience"),
            ("education", "Education"),
            ("skills", "Skills"),
            ("projects", "Projects")
        ]
        missing = [label for key, label in sections if not resume_data.get(key)]
        if not missing:
            return "Your resume contains all key sections and is well-structured."
        else:
            return f"Missing sections: {', '.join(missing)}. Add these to improve content quality."
