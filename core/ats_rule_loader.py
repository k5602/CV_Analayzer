"""
ATSRuleLoader: Loads ATS platform rules from JSON or provides defaults.

Handles ATS platform rules for resume analysis.
If no config file is found, uses built-in defaults.
"""

import os
import json
from loguru import logger
from typing import Dict, Any, Optional

class ATSRuleLoader:
    """
    Loads ATS platform rules from a JSON file or provides default rules.

    This class is used by the ATS analysis engine to get platform-specific parsing rules.
    """

    DEFAULT_PLATFORM = "taleo"

    # If no config file is found, these rules are used for analysis.
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

        ats_rules_path: Path to JSON file containing ATS platform rules.
        """
        self.ats_rules: Dict[str, Any] = {}
        self.ats_rules_path = ats_rules_path
        self.load_rules()

    def load_rules(self):
        """
        Loads ATS platform rules from a config file if available.
        Falls back to built-in defaults if not found or on error.
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
        Returns all loaded ATS platform rules.
        """
        return self.ats_rules

    def get_platform_rule(self, platform: str) -> Dict[str, Any]:
        """
        Returns parsing rules for a specific ATS platform.
        """
        return self.ats_rules.get(platform, self.ats_rules.get(self.DEFAULT_PLATFORM, {}))

    def get_available_platforms(self) -> Dict[str, Any]:
        """
        Returns a dictionary of available ATS platforms and their metadata.
        """
        return {k: v for k, v in self.ats_rules.items()}
