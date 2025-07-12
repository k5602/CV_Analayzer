import os
from typing import Dict, List, Any, Optional, Tuple
from loguru import logger
import json

from models.resume_parser import ResumeParser
from models.ats_checker import ATSChecker
from models.keyword_matcher import KeywordMatcher
from models.feedback_generator import FeedbackGenerator

class AnalyzerController:
    """
    Controller class that orchestrates the resume analysis process by coordinating
    between different model components.
    """

    def __init__(self, ats_rules_path: str = None):
        """
        Initialize the controller with all required model components.

        Args:
            ats_rules_path: Path to the ATS rules configuration file
        """
        logger.info("Initializing AnalyzerController...")

        # If ats_rules_path is None, try to use a default path
        if ats_rules_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ats_rules_path = os.path.join(current_dir, '..', 'config', 'ats_platforms.json')
            if not os.path.exists(ats_rules_path):
                logger.warning(f"Default ATS rules path not found: {ats_rules_path}")
                ats_rules_path = None

        try:
            # Initialize model components
            self.resume_parser = ResumeParser()
            self.ats_checker = ATSChecker(ats_rules_path)
            self.keyword_matcher = KeywordMatcher()
            self.feedback_generator = FeedbackGenerator()

            logger.success("AnalyzerController initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AnalyzerController: {e}")
            raise

    def analyze_resume(self,
                      resume_file_path: str,
                      job_description: str = None,
                      ats_platform: str = None) -> Dict:
        """
        Complete resume analysis process combining all components.

        Args:
            resume_file_path: Path to the resume file (PDF, DOCX, TXT)
            job_description: Optional job description text for matching
            ats_platform: Optional ATS platform to check against (e.g., "taleo")

        Returns:
            Dictionary with complete analysis results
        """
        try:
            # Validate input file exists
            if not os.path.exists(resume_file_path):
                logger.error(f"Resume file not found: {resume_file_path}")
                return {"error": "Resume file not found"}

            # Check if file is a valid type
            ext = os.path.splitext(resume_file_path)[1].lower()
            if ext not in ['.pdf', '.docx', '.doc', '.txt']:
                logger.error(f"Unsupported file format: {ext}")
                return {"error": f"Unsupported file format: {ext}. Please use PDF, DOCX, or TXT files."}

            logger.info(f"Starting analysis for resume: {os.path.basename(resume_file_path)}")

            # Step 1: Parse the resume
            logger.info("Parsing resume...")
            resume_data = self.resume_parser.parse_resume(resume_file_path)

            if "error" in resume_data:
                # Check if it's an OCR-related error
                error_msg = resume_data['error']
                if "OCR" in error_msg or "image" in error_msg:
                    logger.warning(f"OCR-related issue: {error_msg}")
                    # Continue with limited data if possible
                    if not resume_data.get("full_text"):
                        resume_data["full_text"] = "Limited text could be extracted from image-based PDF."
                    # Add a note about OCR limitations
                    resume_data["ocr_limitation"] = True
                else:
                    logger.error(f"Resume parsing error: {error_msg}")
                    return resume_data

            # Step 2: Check ATS compatibility
            logger.info(f"Checking ATS compatibility for platform: {ats_platform or 'default'}")
            ats_analysis = self.ats_checker.analyze_resume(
                resume_data,
                job_description,
                ats_platform
            )

            # Step 3: Match keywords if job description provided
            keyword_analysis = None
            if job_description:
                logger.info("Matching keywords with job description...")
                keyword_analysis = self.keyword_matcher.analyze_skill_match(
                    resume_data,
                    job_description
                )

            # Step 4: Generate comprehensive feedback
            logger.info("Generating feedback...")
            feedback = self.feedback_generator.generate_comprehensive_feedback(
                resume_data,
                ats_analysis,
                keyword_analysis
            )

            # Step 5: Generate section-specific feedback
            section_feedback = self.feedback_generator.generate_section_feedback(resume_data)

            # Step 6: Combine all results into a single response
            result = {
                "resume_data": resume_data,
                "ats_analysis": ats_analysis,
                "keyword_analysis": keyword_analysis,
                "feedback": feedback,
                "section_feedback": section_feedback,
                "scores": {
                    "ats_compatibility": ats_analysis.get("compatibility_score", 0),
                    "overall_match": keyword_analysis.get("overall_match_percentage", 0) if keyword_analysis else None,
                    "skills_match": keyword_analysis.get("skills_match_percentage", 0) if keyword_analysis else None,
                    "experience_match": keyword_analysis.get("experience_match_percentage", 0) if keyword_analysis else None,
                    "education_match": keyword_analysis.get("education_match_percentage", 0) if keyword_analysis else None
                }
            }

            # Add OCR information if applicable
            if resume_data.get("ocr_limitation"):
                result["ocr_used"] = True
                if "feedback" in result and "summary" in result["feedback"]:
                    result["feedback"]["summary"] = "⚠️ LIMITED OCR: " + result["feedback"]["summary"]
                    result["feedback"]["ocr_notice"] = "This resume appears to be image-based. OCR was used to extract text, but results may be limited."

            logger.success(f"Analysis complete for resume: {os.path.basename(resume_file_path)}")
            return result

        except Exception as e:
            logger.error(f"Error during resume analysis: {e}")
            return {"error": f"Error during resume analysis: {str(e)}"}

    def get_available_ats_platforms(self) -> List[Dict]:
        """
        Get a list of available ATS platforms for analysis.

        Returns:
            List of dictionaries with ATS platform information
        """
        platforms = []

        try:
            for platform_id, platform_data in self.ats_checker.ats_rules.items():
                platforms.append({
                    "id": platform_id,
                    "name": platform_data.get("name", platform_id),
                    "description": platform_data.get("description", "")
                })

            return platforms
        except Exception as e:
            logger.error(f"Error getting ATS platforms: {e}")
            return []

    def save_analysis_results(self, analysis_results: Dict, output_path: str) -> bool:
        """
        Save analysis results to a JSON file.

        Args:
            analysis_results: Analysis results dictionary
            output_path: Path to save the results

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Create a serializable version of the results (remove any non-serializable objects)
            serializable_results = {}

            # Only include what's needed for reports and exclude large raw data
            serializable_results["scores"] = analysis_results.get("scores", {})
            serializable_results["feedback"] = analysis_results.get("feedback", {})
            serializable_results["section_feedback"] = analysis_results.get("section_feedback", {})

            if "resume_data" in analysis_results:
                # Copy only essential resume data, excluding full text
                resume_data = analysis_results["resume_data"].copy()
                if "full_text" in resume_data:
                    del resume_data["full_text"]
                serializable_results["resume_data"] = resume_data

            if "ats_analysis" in analysis_results:
                serializable_results["ats_analysis"] = {
                    "compatibility_score": analysis_results["ats_analysis"].get("compatibility_score", 0),
                    "formatting_issues": analysis_results["ats_analysis"].get("formatting_issues", []),
                    "structure_feedback": analysis_results["ats_analysis"].get("structure_feedback", []),
                    "improvement_suggestions": analysis_results["ats_analysis"].get("improvement_suggestions", [])
                }

            if "keyword_analysis" in analysis_results and analysis_results["keyword_analysis"]:
                serializable_results["keyword_analysis"] = {
                    "overall_match_percentage": analysis_results["keyword_analysis"].get("overall_match_percentage", 0),
                    "skill_match_percentage": analysis_results["keyword_analysis"].get("skill_match_percentage", 0),
                    "experience_match_percentage": analysis_results["keyword_analysis"].get("experience_match_percentage", 0),
                    "education_match_percentage": analysis_results["keyword_analysis"].get("education_match_percentage", 0),
                    "skills_match_percentage": analysis_results["keyword_analysis"].get("skills_match_percentage", 0),
                    "matching_keywords": analysis_results["keyword_analysis"].get("matching_keywords", [])[:20],
                    "missing_keywords": analysis_results["keyword_analysis"].get("missing_keywords", [])[:20]
                }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)

            logger.success(f"Analysis results saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")
            return False

    def batch_analyze_resumes(self,
                             resume_file_paths: List[str],
                             job_description: str = None,
                             ats_platform: str = None) -> List[Dict]:
        """
        Analyze multiple resumes at once using multiprocessing for performance.

        Args:
            resume_file_paths: List of paths to resume files
            job_description: Optional job description text for matching
            ats_platform: Optional ATS platform to check against

        Returns:
            List of analysis result dictionaries
        """
        import multiprocessing

        def analyze_worker(file_path):
            logger.info(f"Processing resume: {os.path.basename(file_path)}")
            result = self.analyze_resume(file_path, job_description, ats_platform)
            return {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "analysis": result
            }

        with multiprocessing.Pool(processes=min(4, len(resume_file_paths))) as pool:
            results = pool.map(analyze_worker, resume_file_paths)

        return results
