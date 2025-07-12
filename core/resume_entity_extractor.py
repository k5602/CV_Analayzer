"""
resume_entity_extractor.py
Extracts structured entities from resume text using NLP.
Refactored out of ResumeParser for single-responsibility.
"""

from typing import Dict, List, Any, Optional
from loguru import logger

class ResumeEntityExtractor:
    """
    Extracts entities such as contact info, skills, experience, education, and projects from resume text.
    Uses spaCy NLP if available, otherwise falls back to regex and heuristics.
    """

    def __init__(self, nlp_model: Optional[Any] = None, skills_db: Optional[set] = None):
        """
        Args:
            nlp_model: Optional spaCy NLP model for entity extraction.
            skills_db: Optional set of known skills for matching.
        """
        self.nlp = nlp_model
        self.skills_db = skills_db or set()

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract structured entities from resume text.

        Args:
            text: Resume text.

        Returns:
            Dictionary with extracted entities.
        """
        entities = {
            "contact_info": self._extract_contact_info(text),
            "skills": self._extract_skills(text),
            "experience": self._extract_experience(text),
            "education": self._extract_education(text),
            "projects": self._extract_projects(text),
            "summary": self._extract_summary(text)
        }
        return entities

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        import re
        contact = {}
        # Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            contact["email"] = email_match.group(0)
        # Phone
        phone_match = re.search(r'(\+\d{1,3}[-\.\s]?)?(\(?\d{3}\)?[-\.\s]?\d{3}[-\.\s]?\d{4}|\d{10})', text)
        if phone_match:
            contact["phone"] = phone_match.group(0)
        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text)
        if linkedin_match:
            contact["linkedin"] = linkedin_match.group(0)
        # GitHub
        github_match = re.search(r'github\.com/[\w-]+', text)
        if github_match:
            contact["github"] = github_match.group(0)
        # Name (heuristic: first line or NLP)
        lines = text.strip().split('\n')
        if lines:
            contact["name"] = lines[0].strip()
        return contact

    def _extract_skills(self, text: str) -> List[str]:
        skills_found = []
        text_lower = text.lower()
        for skill in self.skills_db:
            if skill in text_lower:
                skills_found.append(skill)
        # Heuristic: look for "Skills" section
        import re
        skills_section = re.search(r'(skills|expertise|proficiency|competency)[\s:]*([\w\s,;.-]+)', text_lower)
        if skills_section:
            possible_skills = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#\-.]*[a-zA-Z0-9]\b', skills_section.group(2))
            for skill in possible_skills:
                if skill not in skills_found and len(skill) > 2:
                    skills_found.append(skill)
        return list(set(skills_found))

    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        import re
        experiences = []
        # Heuristic: split by "Experience" section headers
        exp_sections = re.split(r'(?:experience|employment|work history|career|professional)[\s:]*', text, flags=re.IGNORECASE)
        for section in exp_sections[1:]:
            # Find job titles, companies, dates, and descriptions
            job_title = None
            company = None
            date_range = None
            description = None
            # Job title (heuristic: first capitalized phrase)
            title_match = re.search(r'\b([A-Z][a-zA-Z\s]+)\b', section)
            if title_match:
                job_title = title_match.group(1)
            # Company (heuristic: "at" or next capitalized phrase)
            company_match = re.search(r'at\s+([A-Z][a-zA-Z\s]+)', section)
            if company_match:
                company = company_match.group(1)
            # Date range
            date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}\s*(-|–|to)\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}', section)
            if date_match:
                date_range = date_match.group(0)
            # Description (heuristic: lines after title/company/date)
            desc_lines = section.split('\n')[1:]
            description = ' '.join([line.strip() for line in desc_lines if line.strip()])
            experiences.append({
                "title": job_title,
                "company": company,
                "date_range": date_range,
                "description": description
            })
        return experiences

    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        import re
        educations = []
        edu_sections = re.split(r'(?:education|academic|qualification)[\s:]*', text, flags=re.IGNORECASE)
        for section in edu_sections[1:]:
            degree = None
            institution = None
            date_range = None
            description = None
            degree_match = re.search(r'(Bachelor|Master|PhD|Associate|B\.Sc\.|M\.Sc\.|Bachelors|Masters|Doctorate)[\w\s,.]*', section, re.IGNORECASE)
            if degree_match:
                degree = degree_match.group(0)
            institution_match = re.search(r'at\s+([A-Z][a-zA-Z\s]+)', section)
            if institution_match:
                institution = institution_match.group(1)
            date_match = re.search(r'\d{4}', section)
            if date_match:
                date_range = date_match.group(0)
            desc_lines = section.split('\n')[1:]
            description = ' '.join([line.strip() for line in desc_lines if line.strip()])
            educations.append({
                "degree": degree,
                "institution": institution,
                "date_range": date_range,
                "description": description
            })
        return educations

    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        import re
        projects = []
        proj_sections = re.split(r'(?:projects|portfolio|works)[\s:]*', text, flags=re.IGNORECASE)
        for section in proj_sections[1:]:
            name = None
            description = None
            techs = []
            name_match = re.search(r'\b([A-Z][a-zA-Z0-9\s]+)\b', section)
            if name_match:
                name = name_match.group(1)
            tech_matches = re.findall(r'(python|java|react|node\.js|sql|aws|docker|kubernetes)', section, re.IGNORECASE)
            techs = list(set([tech.lower() for tech in tech_matches]))
            desc_lines = section.split('\n')[1:]
            description = ' '.join([line.strip() for line in desc_lines if line.strip()])
            projects.append({
                "name": name,
                "description": description,
                "technologies": techs
            })
        return projects

    def _extract_summary(self, text: str) -> str:
        import re
        summary_match = re.search(r'(summary|objective|profile|about)[\s:]*([\w\s,;.-]+)', text, re.IGNORECASE)
        if summary_match:
            return summary_match.group(2).strip()
        # Fallback: first paragraph
        paragraphs = text.strip().split('\n\n')
        if paragraphs:
            return paragraphs[0].strip()
        return ""
