"""
ATSRuleLoader: Loads ATS platform rules from JSON or provides defaults.
Refactored out of ATSChecker for single-responsibility.
"""

import os
import json
from loguru import logger
from typing import Dict, Any, Optional

class ATSRuleLoader:
    """
    Loads ATS platform rules from a JSON file or provides default rules.
    """

    DEFAULT_PLATFORM = "taleo"

    DEFAULT_RULES = {
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

    def __init__(self, ats_rules_path: Optional[str] = None):
        """
        Initialize the rule loader and load rules from file or defaults.
        Args:
            ats_rules_path: Path to JSON file containing ATS platform rules
        """
        self.ats_rules: Dict[str, Any] = {}
        self.ats_rules_path = ats_rules_path
        self.load_rules()

    def load_rules(self):
        """
        Load ATS platform rules from JSON file, or use defaults if not available.
        """
        if self.ats_rules_path and os.path.exists(self.ats_rules_path):
            try:
                with open(self.ats_rules_path, 'r', encoding='utf-8') as f:
                    self.ats_rules = json.load(f)
                logger.success(f"Loaded ATS rules from {self.ats_rules_path}")
            except Exception as e:
                logger.error(f"Error loading ATS rules: {e}")
                self.ats_rules = self.DEFAULT_RULES.copy()
                logger.info("Loaded default ATS rules due to error.")
        else:
            logger.warning(f"ATS rules path not found: {self.ats_rules_path}")
            self.ats_rules = self.DEFAULT_RULES.copy()
            logger.info("Loaded default ATS rules.")

    def get_rules(self) -> Dict[str, Any]:
        """
        Get all loaded ATS platform rules.
        Returns:
            Dictionary of ATS platform rules.
        """
        return self.ats_rules

    def get_platform_rule(self, platform: str) -> Dict[str, Any]:
        """
        Get rules for a specific ATS platform.
        Args:
            platform: Platform key (e.g., "taleo")
        Returns:
            Dictionary of parsing rules for the platform.
        """
        return self.ats_rules.get(platform, self.ats_rules.get(self.DEFAULT_PLATFORM, {}))

    def get_available_platforms(self) -> Dict[str, Any]:
        """
        Get a dictionary of available ATS platforms and their metadata.
        Returns:
            Dictionary of platform metadata.
        """
        return {k: v for k, v in self.ats_rules.items()}
