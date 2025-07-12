# Base class for ATS platform plugins.
# Extend this for each ATS integration.

from abc import ABC, abstractmethod
from typing import Dict, Any

class ATSPlatformBase(ABC):
    """
    Extend this class for each ATS platform.
    Only override methods relevant to your platform.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Platform name for UI display."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Short description for UI/help."""
        pass

    @abstractmethod
    def get_parsing_rules(self) -> Dict[str, Any]:
        """Return parsing rules (section order, formatting, etc)."""
        pass

    @abstractmethod
    def analyze_resume(self, resume_data: Dict[str, Any], job_description: str = None) -> Dict[str, Any]:
        """
        Main entry for ATS analysis.
        Return a dict with scores, issues, and suggestions.
        """
        pass
