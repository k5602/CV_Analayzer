# Abstract base class for pluggable ATS platform implementations

from abc import ABC, abstractmethod
from typing import Dict, Any

class ATSPlatformBase(ABC):
    """
    Abstract base class for ATS platform implementations.
    Each ATS platform should inherit from this class and implement required methods.
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the name of the ATS platform.
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Returns a brief description of the ATS platform.
        """
        pass

    @abstractmethod
    def get_parsing_rules(self) -> Dict[str, Any]:
        """
        Returns the parsing rules for the ATS platform.
        """
        pass

    @abstractmethod
    def analyze_resume(self, resume_data: Dict[str, Any], job_description: str = None) -> Dict[str, Any]:
        """
        Analyzes the resume data according to the platform's rules.

        Args:
            resume_data: Structured resume information.
            job_description: Optional job description for keyword matching.

        Returns:
            Dictionary containing ATS compatibility analysis results.
        """
        pass
