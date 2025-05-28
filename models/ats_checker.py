import re
import json
import os
from typing import Dict, List, Tuple, Any, Optional
from loguru import logger


class ATSChecker:
    """
    A class to analyze resume compatibility with Applicant Tracking Systems (ATS)
    and provide feedback for optimization.
    """

    def __init__(self, ats_rules_path: str = None):
        """
        Initialize the ATS checker with platform-specific rules.
        
        Args:
            ats_rules_path: Path to JSON file containing ATS platform rules
        """
        self.ats_rules = {}
        self.default_platform = "taleo"  # Default platform if none specified
        
        # Load ATS platform rules
        if ats_rules_path and os.path.exists(ats_rules_path):
            try:
                with open(ats_rules_path, 'r', encoding='utf-8') as f:
                    self.ats_rules = json.load(f)
                logger.success(f"Loaded ATS rules from {ats_rules_path}")
            except Exception as e:
                logger.error(f"Error loading ATS rules: {e}")
                self._load_default_rules()
        else:
            logger.warning(f"ATS rules path not found: {ats_rules_path}")
            self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default ATS rules if external file is not available."""
        self.ats_rules = {
            "taleo": {
                "name": "Taleo",
                "description": "One of the most popular ATS, used by large corporations",
                "parsing_rules": {
                    "preferred_format": "chronological",
                    "section_headings": ["Education", "Experience", "Skills", "Projects"],
                    "keywords_importance": "high",
                    "formatting_preferences": {
                        "bullet_points": True,
                        "tables": False,
                        "images": False,
                        "headers_footers": False,
                        "columns": False,
                        "fancy_fonts": False
                    },
                    "file_preferences": ["pdf", "docx", "txt"],
                    "recommended_fonts": ["Arial", "Times New Roman", "Calibri"],
                    "special_notes": "Emphasizes chronological work history and keywords matching job description"
                }
            }
        }
        logger.info("Loaded default ATS rules")
    
    def analyze_resume(self, resume_data: Dict, job_description: str = None, ats_platform: str = None) -> Dict:
        """
        Analyze resume for ATS compatibility and provide feedback.
        
        Args:
            resume_data: Parsed resume data dictionary
            job_description: Optional job description text to match against
            ats_platform: Name of the ATS platform to check against (e.g., "taleo")
            
        Returns:
            Dictionary containing analysis results and feedback
        """
        if not ats_platform or ats_platform not in self.ats_rules:
            ats_platform = self.default_platform
            if ats_platform not in self.ats_rules:
                logger.error(f"Default ATS platform rules not found: {ats_platform}")
                return {"error": "ATS platform rules not available"}
        
        platform_rules = self.ats_rules[ats_platform]
        
        # Prepare the result structure
        result = {
            "ats_platform": platform_rules["name"],
            "compatibility_score": 0,
            "keyword_match": {
                "score": 0,
                "matching_keywords": [],
                "missing_keywords": []
            },
            "formatting_issues": [],
            "structure_feedback": [],
            "improvement_suggestions": [],
            "detailed_scores": {
                "keyword_match": 0,
                "formatting": 0,
                "structure": 0,
                "file_type": 0
            }
        }
        
        # Check file format compatibility
        result["detailed_scores"]["file_type"] = self._check_file_format(
            resume_data.get("file_format", {}),
            platform_rules["parsing_rules"]["file_preferences"]
        )
        
        # Check formatting issues
        formatting_score, formatting_issues = self._check_formatting(
            resume_data,
            platform_rules["parsing_rules"]["formatting_preferences"]
        )
        result["detailed_scores"]["formatting"] = formatting_score
        result["formatting_issues"] = formatting_issues
        
        # Check document structure
        structure_score, structure_feedback = self._check_structure(
            resume_data,
            platform_rules["parsing_rules"]["section_headings"],
            platform_rules["parsing_rules"]["preferred_format"]
        )
        result["detailed_scores"]["structure"] = structure_score
        result["structure_feedback"] = structure_feedback
        
        # Check keyword match if job description provided
        if job_description:
            keyword_score, matching, missing = self._check_keyword_match(
                resume_data,
                job_description,
                platform_rules["parsing_rules"]["keywords_importance"]
            )
            result["detailed_scores"]["keyword_match"] = keyword_score
            result["keyword_match"]["score"] = keyword_score
            result["keyword_match"]["matching_keywords"] = matching
            result["keyword_match"]["missing_keywords"] = missing
        
        # Calculate overall ATS compatibility score
        # Weights: keyword_match (40%), formatting (30%), structure (20%), file_type (10%)
        weights = {
            "keyword_match": 0.4 if job_description else 0,
            "formatting": 0.3 if job_description else 0.5,
            "structure": 0.2 if job_description else 0.3,
            "file_type": 0.1 if job_description else 0.2
        }
        
        overall_score = sum(
            score * weights[key] 
            for key, score in result["detailed_scores"].items()
        )
        
        if not job_description:
            # Normalize score when no job description is provided (max score would be 60% otherwise)
            overall_score = overall_score / sum(weights.values())
            
        result["compatibility_score"] = round(overall_score)
        
        # Generate improvement suggestions
        result["improvement_suggestions"] = self._generate_suggestions(
            result,
            platform_rules
        )
        
        return result
    
    def _check_file_format(self, file_format: Dict, preferred_formats: List[str]) -> int:
        """
        Check if the resume's file format is ATS-friendly.
        
        Returns:
            Score between 0-100
        """
        if not file_format:
            return 50  # No information
            
        extension = file_format.get("extension", "").lower().lstrip(".")
        
        if extension in preferred_formats:
            # Find the position in the preference list (earlier is better)
            position = preferred_formats.index(extension)
            
            # Calculate score based on position (first position gets 100, last gets 60)
            score = 100 - (40 * position / max(1, len(preferred_formats) - 1))
            
            # Check for problematic elements
            if file_format.get("has_problematic_elements", False):
                score -= 30
                
            return int(score)
        else:
            # Not in the preferred list
            if extension in ["pdf", "docx", "txt"]:
                return 50  # Common format but not preferred
            else:
                return 20  # Uncommon format
    
    def _check_formatting(self, resume_data: Dict, formatting_prefs: Dict) -> Tuple[int, List[str]]:
        """
        Check resume for formatting issues that might affect ATS parsing.
        
        Returns:
            Tuple of (score between 0-100, list of formatting issues)
        """
        issues = []
        
        # Check for problematic elements in file
        if resume_data.get("file_format", {}).get("has_problematic_elements", False):
            if not formatting_prefs.get("tables", False):
                issues.append("Contains tables or complex formatting that may confuse ATS")
            
            if not formatting_prefs.get("images", False):
                issues.append("Contains images or graphics that ATS cannot parse")
        
        # Check for bullet points (if preferred)
        has_bullet_points = False
        full_text = resume_data.get("full_text", "")
        
        if full_text:
            bullet_patterns = [r'•', r'·', r'‣', r'⁃', r'⦿', r'⦾', r'-', r'\*', r'✓', r'✔', r'➢', r'➤']
            for pattern in bullet_patterns:
                if re.search(pattern, full_text):
                    has_bullet_points = True
                    break
        
        if formatting_prefs.get("bullet_points", True) and not has_bullet_points:
            issues.append("Lacks bullet points for better readability and parsing")
        
        # Check for multi-column layout (approximation)
        # This is a simplified check, would need layout analysis for better detection
        if not formatting_prefs.get("columns", False):
            # Detect multiple columns by checking for text alignment patterns
            if full_text and len(full_text.split('\n')) > 10:
                lines = full_text.split('\n')
                indentation_counts = {}
                
                for line in lines:
                    if line.strip():
                        leading_spaces = len(line) - len(line.lstrip())
                        indentation_counts[leading_spaces] = indentation_counts.get(leading_spaces, 0) + 1
                
                # If there are multiple common indentation levels with high frequency
                common_indents = sorted([(count, indent) for indent, count in indentation_counts.items()], reverse=True)
                
                if len(common_indents) >= 3 and common_indents[1][0] > len(lines) * 0.15:
                    # Second most common indentation used for >15% of lines could indicate columns
                    issues.append("May contain multi-column layout which can confuse ATS parsing")
        
        # Calculate score based on issues
        if not issues:
            return 100, issues
        
        # Deduct points based on number and severity of issues
        base_score = 100
        deduction_per_issue = 100 / (len(formatting_prefs) + 1)  # +1 to avoid division by zero
        
        score = max(0, base_score - (len(issues) * deduction_per_issue))
        return int(score), issues
    
    def _check_structure(self, resume_data: Dict, preferred_sections: List[str], 
                        preferred_format: str) -> Tuple[int, List[str]]:
        """
        Check the resume structure against ATS preferences.
        
        Returns:
            Tuple of (score between 0-100, list of structure feedback items)
        """
        feedback = []
        
        # Check for presence of key sections
        found_sections = []
        
        if resume_data.get("contact_info") and resume_data["contact_info"].get("name"):
            found_sections.append("Contact Information")
        else:
            feedback.append("Missing or incomplete contact information")
        
        if resume_data.get("summary"):
            found_sections.append("Summary/Objective")
        
        if resume_data.get("experience") and len(resume_data["experience"]) > 0:
            found_sections.append("Experience")
        else:
            feedback.append("Missing work experience section")
        
        if resume_data.get("education") and len(resume_data["education"]) > 0:
            found_sections.append("Education")
        else:
            feedback.append("Missing education section")
        
        if resume_data.get("skills") and len(resume_data["skills"]) > 0:
            found_sections.append("Skills")
        else:
            feedback.append("Missing skills section")
        
        # Check section order matches preferred format
        if preferred_format == "chronological":
            # For chronological, check if experience is before skills
            exp_pos = -1
            skills_pos = -1
            full_text = resume_data.get("full_text", "").lower()
            
            # Very simplified check - would need better section detection in practice
            exp_match = re.search(r'experience|employment|work history', full_text)
            if exp_match:
                exp_pos = exp_match.start()
                
            skills_match = re.search(r'skills|expertise|competencies', full_text)
            if skills_match:
                skills_pos = skills_match.start()
            
            if exp_pos > 0 and skills_pos > 0 and skills_pos < exp_pos:
                feedback.append("For chronological format, work experience should come before skills section")
        
        # Calculate score based on sections found and feedback
        expected_section_count = 5  # Contact, Summary, Experience, Education, Skills
        found_section_count = len(found_sections)
        
        section_score = (found_section_count / expected_section_count) * 100
        
        # Reduce score for each piece of structural feedback
        feedback_penalty = min(40, 10 * len(feedback))
        
        score = max(0, section_score - feedback_penalty)
        return int(score), feedback
    
    def _check_keyword_match(self, resume_data: Dict, job_description: str, 
                           keyword_importance: str) -> Tuple[int, List[str], List[str]]:
        """
        Check how well resume keywords match job description.
        
        Returns:
            Tuple of (score between 0-100, matching keywords list, missing keywords list)
        """
        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_description)
        
        # Get all text content from resume
        resume_text = resume_data.get("full_text", "")
        if not resume_text:
            resume_text = " ".join([
                str(resume_data.get("summary", "")),
                " ".join(str(exp.get("description", "")) for exp in resume_data.get("experience", [])),
                " ".join(str(skill) for skill in resume_data.get("skills", []))
            ])
        
        resume_text = resume_text.lower()
        
        # Check for keyword matches
        matching_keywords = []
        missing_keywords = []
        
        for keyword in job_keywords:
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', resume_text):
                matching_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate match percentage
        if not job_keywords:
            return 50, matching_keywords, missing_keywords  # No keywords to match
        
        match_percentage = len(matching_keywords) / len(job_keywords) * 100
        
        # Apply importance weighting
        if keyword_importance == "high":
            # More strict scoring for high importance
            if match_percentage < 30:
                match_percentage *= 0.7  # Larger penalty for poor match
        elif keyword_importance == "medium":
            # Standard scoring
            pass
        else:  # low
            # More lenient scoring
            if match_percentage < 50:
                match_percentage = match_percentage * 0.8 + 20  # Boost lower scores
        
        return int(match_percentage), matching_keywords, missing_keywords
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from job description.
        This is a simple implementation; a more advanced approach would use NLP.
        
        Returns:
            List of extracted keywords
        """
        # For this implementation, we'll use common skill/job keywords and filtering
        # In a real implementation, you would use KeyBERT or similar NLP approach
        
        # Convert to lowercase and tokenize
        text = text.lower()
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#\-.]*[a-zA-Z0-9]\b', text)
        
        # Filter out common stop words
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what', 'when',
            'where', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'to', 'from', 'by',
            'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off',
            'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
            'why', 'how', 'all', 'any', 'both', 'each', 'other', 'such'
        }
        
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Count frequencies
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Extract multi-word phrases (simplified approach)
        phrases = []
        text_lower = text.lower()
        
        # Look for common resume keywords
        common_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'sql', 'nosql',
            'aws', 'azure', 'cloud', 'docker', 'kubernetes', 'ci/cd', 'devops', 'machine learning',
            'data science', 'data analysis', 'artificial intelligence', 'deep learning',
            'project management', 'agile', 'scrum', 'team lead', 'leadership', 'communication',
            'problem solving', 'critical thinking', 'collaboration', 'customer service',
            'database', 'front-end', 'back-end', 'full-stack', 'testing', 'qa', 'ux', 'ui',
            'product management', 'mobile development', 'android', 'ios', 'react native',
            'flask', 'django', 'spring boot', 'mongodb', 'postgresql', 'mysql', 'git',
            'linux', 'unix', 'networking', 'security', 'api', 'rest', 'graphql', 'html', 'css',
            'sass', 'less', 'typescript', 'golang', 'rust', 'c++', 'c#', '.net'
        ]
        
        for skill in common_skills:
            if skill in text_lower:
                phrases.append(skill)
        
        # Combine single words and phrases, giving preference to multi-word phrases
        keywords = []
        
        # Add most frequent single words (if they're not part of phrases)
        sorted_words = sorted([(freq, word) for word, freq in word_freq.items()], reverse=True)
        for freq, word in sorted_words[:15]:  # Get top 15 most frequent words
            # Only add if it's not already part of a phrase
            if not any(word in phrase for phrase in phrases):
                keywords.append(word)
        
        # Add all identified phrases
        keywords.extend(phrases)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        # Limit to top 20 keywords
        return unique_keywords[:20]
    
    def _generate_suggestions(self, analysis_result: Dict, platform_rules: Dict) -> List[str]:
        """
        Generate specific improvement suggestions based on the analysis.
        
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        # Suggestions based on score components
        scores = analysis_result["detailed_scores"]
        
        # Keyword match suggestions
        if "keyword_match" in scores and scores["keyword_match"] < 60:
            # Add missing keywords suggestion
            if analysis_result["keyword_match"]["missing_keywords"]:
                top_missing = analysis_result["keyword_match"]["missing_keywords"][:5]
                suggestions.append(
                    f"Add these keywords from the job description: {', '.join(top_missing)}"
                )
        
        # File format suggestions
        if scores["file_type"] < 70:
            preferred_formats = platform_rules["parsing_rules"]["file_preferences"]
            suggestions.append(
                f"Use a preferred file format: {preferred_formats[0].upper()} "
                f"(other acceptable formats: {', '.join(f.upper() for f in preferred_formats[1:])})."
            )
        
        # Formatting suggestions
        if scores["formatting"] < 70:
            for issue in analysis_result["formatting_issues"]:
                suggestions.append(f"Fix formatting issue: {issue}")
            
            # Add font recommendation
            if "recommended_fonts" in platform_rules["parsing_rules"]:
                fonts = platform_rules["parsing_rules"]["recommended_fonts"]
                suggestions.append(f"Use ATS-friendly fonts: {', '.join(fonts)}")
        
        # Structure suggestions
        if scores["structure"] < 70:
            for feedback in analysis_result["structure_feedback"]:
                suggestions.append(feedback)
            
            # Recommend section headers
            if "section_headings" in platform_rules["parsing_rules"]:
                sections = platform_rules["parsing_rules"]["section_headings"]
                suggestions.append(
                    f"Use standard section headers in this order: {', '.join(sections)}"
                )
        
        # General suggestions
        suggestions.append(
            "Ensure your resume has clear section headings and concise bullet points."
        )
        
        if platform_rules["parsing_rules"].get("preferred_format") == "chronological":
            suggestions.append(
                "Use a chronological format with your most recent experience first."
            )
        
        if not suggestions:
            suggestions.append(
                "Your resume appears to be well-optimized for ATS systems. Continue to tailor it for specific job descriptions."
            )
        
        return suggestions