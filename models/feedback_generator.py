import os
from typing import Dict, List, Tuple, Any, Optional
from loguru import logger

class FeedbackGenerator:
    """
    A class to generate comprehensive feedback on resumes based on ATS analysis and keyword matching.
    Provides actionable recommendations for improvement.
    """
    
    def __init__(self):
        """Initialize the FeedbackGenerator with feedback templates and settings."""
        self.feedback_templates = {
            "missing_keywords": "Your resume is missing these important keywords: {keywords}. Consider adding them.",
            "format_issues": "There are formatting issues that might affect ATS parsing: {issues}",
            "section_missing": "Your resume is missing a critical section: {section}",
            "low_match": "Your resume shows only {score}% match with the job description. Aim for at least 70%.",
            "ats_score": "Your resume has an ATS Compatibility Score of {score}/100.",
            "positive": "Strong points: {points}"
        }
    
    def generate_comprehensive_feedback(self,
                                       resume_data: Dict,
                                       ats_analysis: Dict,
                                       keyword_analysis: Dict = None) -> Dict:
        """
        Generate comprehensive feedback on the resume based on all analyses.
        
        Args:
            resume_data: Parsed resume data dictionary
            ats_analysis: Results from ATS compatibility analysis
            keyword_analysis: Optional results from keyword matching analysis
            
        Returns:
            Dictionary with structured feedback
        """
        try:
            # Initialize feedback structure
            feedback = {
                "summary": "",
                "ats_compatibility": {
                    "score": ats_analysis.get("compatibility_score", 0),
                    "issues": [],
                    "recommendations": []
                },
                "content_quality": {
                    "strengths": [],
                    "weaknesses": [],
                    "recommendations": []
                },
                "keyword_match": {
                    "score": 0,
                    "matched_keywords": [],
                    "missing_keywords": [],
                    "recommendations": []
                },
                "section_feedback": {}
            }
            
            # Add ATS compatibility feedback
            self._add_ats_compatibility_feedback(feedback, ats_analysis)
            
            # Add content quality feedback
            self._add_content_quality_feedback(feedback, resume_data)
            
            # Add keyword match feedback if available
            if keyword_analysis:
                self._add_keyword_match_feedback(feedback, keyword_analysis)
                
            # Generate summary feedback
            feedback["summary"] = self._generate_summary_feedback(feedback, ats_analysis, keyword_analysis)
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            return {
                "error": f"Error generating feedback: {str(e)}",
                "summary": "Could not generate complete feedback due to an error."
            }
    
    def _add_ats_compatibility_feedback(self, feedback: Dict, ats_analysis: Dict):
        """Add ATS compatibility feedback to the feedback dict."""
        # Add ATS score
        feedback["ats_compatibility"]["score"] = ats_analysis.get("compatibility_score", 0)
        
        # Add formatting issues
        for issue in ats_analysis.get("formatting_issues", []):
            feedback["ats_compatibility"]["issues"].append(issue)
        
        # Add structure feedback
        for structure_item in ats_analysis.get("structure_feedback", []):
            feedback["ats_compatibility"]["issues"].append(structure_item)
        
        # Add recommendations
        for suggestion in ats_analysis.get("improvement_suggestions", []):
            feedback["ats_compatibility"]["recommendations"].append(suggestion)
            
        # If no issues found, add positive feedback
        if not feedback["ats_compatibility"]["issues"]:
            feedback["ats_compatibility"]["issues"].append(
                "No major ATS compatibility issues detected."
            )
    
    def _add_content_quality_feedback(self, feedback: Dict, resume_data: Dict):
        """Add content quality feedback to the feedback dict."""
        # Check for contact information completeness
        contact_info = resume_data.get("contact_info", {})
        if not contact_info.get("email"):
            feedback["content_quality"]["weaknesses"].append("Missing email address")
            feedback["content_quality"]["recommendations"].append("Add a professional email address")
        
        if not contact_info.get("phone"):
            feedback["content_quality"]["weaknesses"].append("Missing phone number")
            feedback["content_quality"]["recommendations"].append("Add a phone number")
            
        if not contact_info.get("linkedin"):
            feedback["content_quality"]["recommendations"].append("Consider adding your LinkedIn profile URL")
        
        # Check experience descriptions
        experience = resume_data.get("experience", [])
        weak_experience = 0
        for exp in experience:
            desc = exp.get("description", "")
            if not desc or len(desc) < 50:
                weak_experience += 1
                
        if weak_experience > 0:
            feedback["content_quality"]["weaknesses"].append(
                f"{weak_experience} job entries have minimal or missing descriptions"
            )
            feedback["content_quality"]["recommendations"].append(
                "Add more detailed descriptions of your work experience using action verbs and quantifiable achievements"
            )
        
        # Check skills
        skills = resume_data.get("skills", [])
        if not skills or len(skills) < 5:
            feedback["content_quality"]["weaknesses"].append("Limited or missing skills section")
            feedback["content_quality"]["recommendations"].append(
                "Add a comprehensive skills section with relevant technical and soft skills"
            )
        else:
            feedback["content_quality"]["strengths"].append(
                f"Good skills section with {len(skills)} identified skills"
            )
        
        # Check education
        education = resume_data.get("education", [])
        if not education:
            feedback["content_quality"]["weaknesses"].append("Missing education section")
            feedback["content_quality"]["recommendations"].append("Add your educational background")
            
        # Check summary/objective
        summary = resume_data.get("summary", "")
        if not summary or len(summary) < 30:
            feedback["content_quality"]["recommendations"].append(
                "Add a concise professional summary highlighting your strengths and career goals"
            )
        elif len(summary) > 500:
            feedback["content_quality"]["recommendations"].append(
                "Consider shortening your professional summary to be more concise (aim for 2-4 sentences)"
            )
        else:
            feedback["content_quality"]["strengths"].append("Good professional summary/objective")
            
        # If no weaknesses found, add positive feedback
        if not feedback["content_quality"]["weaknesses"]:
            feedback["content_quality"]["strengths"].append(
                "Overall good content quality with all essential sections present"
            )
            
        # If no strengths identified, add a generic one
        if not feedback["content_quality"]["strengths"]:
            feedback["content_quality"]["strengths"].append(
                "Resume has basic structure in place"
            )
    
    def _add_keyword_match_feedback(self, feedback: Dict, keyword_analysis: Dict):
        """Add keyword match feedback to the feedback dict."""
        # Add score
        overall_match = keyword_analysis.get("overall_match_percentage", 0)
        feedback["keyword_match"]["score"] = overall_match
        
        # Add matched keywords
        feedback["keyword_match"]["matched_keywords"] = keyword_analysis.get("matching_keywords", [])[:10]
        
        # Add missing keywords
        feedback["keyword_match"]["missing_keywords"] = keyword_analysis.get("missing_keywords", [])[:10]
        
        # Add recommendations
        if overall_match < 50:
            feedback["keyword_match"]["recommendations"].append(
                "Your resume needs significant keyword optimization to match the job description"
            )
            if keyword_analysis.get("key_gaps"):
                feedback["keyword_match"]["recommendations"].append(
                    f"Focus on adding these key missing requirements: {', '.join(keyword_analysis.get('key_gaps', [])[:5])}"
                )
        elif overall_match < 70:
            feedback["keyword_match"]["recommendations"].append(
                "Your resume has moderate keyword matching but could be improved"
            )
            if keyword_analysis.get("key_gaps"):
                feedback["keyword_match"]["recommendations"].append(
                    f"Consider adding these requirements: {', '.join(keyword_analysis.get('key_gaps', [])[:3])}"
                )
        else:
            feedback["keyword_match"]["recommendations"].append(
                "Good keyword matching with the job description"
            )
            
        # Add section-specific feedback
        if keyword_analysis.get("experience_match_percentage", 0) < 50:
            feedback["keyword_match"]["recommendations"].append(
                "Your work experience section could better highlight relevant experience for this role"
            )
            
        if keyword_analysis.get("skills_match_percentage", 0) < 60:
            feedback["keyword_match"]["recommendations"].append(
                "Consider updating your skills section to better match the job requirements"
            )
    
    def _generate_summary_feedback(self, feedback: Dict, 
                                 ats_analysis: Dict, 
                                 keyword_analysis: Dict = None) -> str:
        """Generate a summary feedback paragraph."""
        ats_score = ats_analysis.get("compatibility_score", 0)
        match_score = keyword_analysis.get("overall_match_percentage", 0) if keyword_analysis else 0
        
        # Generate beginning of summary based on ATS score
        if ats_score >= 80:
            summary = "Your resume is well-optimized for ATS systems. "
        elif ats_score >= 60:
            summary = "Your resume is moderately optimized for ATS systems with some room for improvement. "
        else:
            summary = "Your resume needs significant optimization for ATS systems. "
            
        # Add keyword matching information if available
        if keyword_analysis:
            if match_score >= 80:
                summary += "It shows excellent alignment with the job requirements. "
            elif match_score >= 60:
                summary += "It shows decent alignment with the job requirements, but could be improved. "
            else:
                summary += "It shows low alignment with the job requirements and needs significant tailoring. "
                
        # Add most critical recommendations
        recommendations = []
        
        # Include top ATS recommendation
        if feedback["ats_compatibility"]["recommendations"]:
            recommendations.append(feedback["ats_compatibility"]["recommendations"][0])
            
        # Include top content recommendation
        if feedback["content_quality"]["recommendations"]:
            recommendations.append(feedback["content_quality"]["recommendations"][0])
            
        # Include top keyword recommendation if available
        if keyword_analysis and feedback["keyword_match"]["recommendations"]:
            recommendations.append(feedback["keyword_match"]["recommendations"][0])
            
        if recommendations:
            summary += "Key recommendations: " + " ".join(recommendations)
            
        return summary

    def generate_section_feedback(self, resume_data: Dict) -> Dict[str, List[str]]:
        """
        Generate specific feedback for each resume section.
        
        Args:
            resume_data: Parsed resume data dictionary
            
        Returns:
            Dictionary with feedback for each section
        """
        section_feedback = {}
        
        # Contact information feedback
        contact_info = resume_data.get("contact_info", {})
        contact_feedback = []
        
        if not contact_info.get("name"):
            contact_feedback.append("Make sure your full name is clearly visible at the top of your resume")
            
        if not contact_info.get("email"):
            contact_feedback.append("Add a professional email address")
        
        if not contact_info.get("phone"):
            contact_feedback.append("Include a phone number where employers can reach you")
            
        if not contact_info.get("linkedin"):
            contact_feedback.append("Consider adding your LinkedIn profile URL")
            
        if not contact_info.get("location"):
            contact_feedback.append("Include your city and state/country")
            
        if not contact_feedback:
            contact_feedback.append("Contact information is complete")
            
        section_feedback["contact_information"] = contact_feedback
        
        # Summary feedback
        summary = resume_data.get("summary", "")
        summary_feedback = []
        
        if not summary:
            summary_feedback.append("Add a professional summary or objective statement")
        elif len(summary) < 50:
            summary_feedback.append("Expand your professional summary to highlight your key qualifications")
        elif len(summary) > 500:
            summary_feedback.append("Consider shortening your professional summary to be more concise")
        else:
            # Check for action words
            action_words = ["achieved", "improved", "developed", "managed", "created", "implemented", "led", "increased", "reduced", "delivered"]
            has_action_word = any(word in summary.lower() for word in action_words)
            
            if not has_action_word:
                summary_feedback.append("Use strong action verbs in your summary to demonstrate impact")
            else:
                summary_feedback.append("Good professional summary with action-oriented language")
                
        section_feedback["summary"] = summary_feedback
        
        # Work experience feedback
        experience = resume_data.get("experience", [])
        experience_feedback = []
        
        if not experience:
            experience_feedback.append("Add your work experience section")
        else:
            exp_with_dates = sum(1 for exp in experience if exp.get("date_range"))
            if exp_with_dates < len(experience):
                experience_feedback.append("Include dates for all work experiences")
                
            exp_with_description = sum(1 for exp in experience if exp.get("description") and len(exp.get("description", "")) > 50)
            if exp_with_description < len(experience):
                experience_feedback.append("Add detailed descriptions for all positions using bullet points and action verbs")
                
            if experience and all(len(exp.get("description", "")) > 50 for exp in experience):
                experience_feedback.append("Good detailed work experience section")
                
        section_feedback["experience"] = experience_feedback
        
        # Skills feedback
        skills = resume_data.get("skills", [])
        skills_feedback = []
        
        if not skills:
            skills_feedback.append("Add a dedicated skills section")
        elif len(skills) < 5:
            skills_feedback.append("List more relevant skills (aim for at least 8-12 key skills)")
        elif len(skills) > 20:
            skills_feedback.append("Consider focusing on your most relevant skills rather than listing too many")
        else:
            skills_feedback.append("Good skills section with an appropriate number of skills")
            
        # Check for technical vs soft skills balance
        technical_keywords = {"python", "java", "javascript", "html", "css", "aws", "azure", "sql", "nosql", "react", "angular", "vue", "django", "flask"}
        soft_keywords = {"communication", "leadership", "teamwork", "problem solving", "critical thinking", "time management", "project management"}
        
        technical_count = sum(1 for skill in skills if any(tech in skill.lower() for tech in technical_keywords))
        soft_count = sum(1 for skill in skills if any(soft in skill.lower() for soft in soft_keywords))
        
        if technical_count == 0 and soft_count > 0:
            skills_feedback.append("Consider adding technical skills to balance your soft skills")
        elif technical_count > 0 and soft_count == 0:
            skills_feedback.append("Consider adding some soft skills to complement your technical skills")
            
        section_feedback["skills"] = skills_feedback
        
        # Education feedback
        education = resume_data.get("education", [])
        education_feedback = []
        
        if not education:
            education_feedback.append("Add your educational background")
        else:
            edu_with_dates = sum(1 for edu in education if edu.get("date_range"))
            if edu_with_dates < len(education):
                education_feedback.append("Include graduation dates for all educational entries")
                
            edu_with_degree = sum(1 for edu in education if edu.get("degree"))
            if edu_with_degree < len(education):
                education_feedback.append("Specify degree types for all educational entries")
                
            edu_with_institution = sum(1 for edu in education if edu.get("institution"))
            if edu_with_institution < len(education):
                education_feedback.append("Include institution names for all educational entries")
                
            if all(edu.get("degree") and edu.get("institution") and edu.get("date_range") for edu in education):
                education_feedback.append("Education section is well-structured")
                
        section_feedback["education"] = education_feedback
        
        # Projects feedback
        projects = resume_data.get("projects", [])
        projects_feedback = []
        
        if projects:
            projects_with_tech = sum(1 for proj in projects if proj.get("technologies") and len(proj.get("technologies", [])) > 0)
            if projects_with_tech < len(projects):
                projects_feedback.append("List technologies used for each project")
                
            if all(proj.get("name") and len(proj.get("description", "")) > 30 for proj in projects):
                projects_feedback.append("Projects are well documented with names and descriptions")
                
        section_feedback["projects"] = projects_feedback
        
        # Certifications feedback
        certifications = resume_data.get("certifications", [])
        certifications_feedback = []
        
        if certifications:
            certifications_feedback.append(f"Good inclusion of {len(certifications)} certifications")
            
        section_feedback["certifications"] = certifications_feedback
        
        return section_feedback