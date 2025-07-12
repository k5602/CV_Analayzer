# Centralized custom exception classes for CV Analyzer

class CVAnalyzerError(Exception):
    """Base exception for all CV Analyzer errors."""
    pass

class ResumeParsingError(CVAnalyzerError):
    """Raised when resume parsing fails."""
    def __init__(self, message, file_path=None):
        super().__init__(message)
        self.file_path = file_path

class ATSAnalysisError(CVAnalyzerError):
    """Raised when ATS analysis fails."""
    def __init__(self, message, platform=None):
        super().__init__(message)
        self.platform = platform

class KeywordMatchingError(CVAnalyzerError):
    """Raised when keyword matching fails."""
    def __init__(self, message, job_description=None):
        super().__init__(message)
        self.job_description = job_description

class FeedbackGenerationError(CVAnalyzerError):
    """Raised when feedback generation fails."""
    def __init__(self, message):
        super().__init__(message)

class DependencyValidationError(CVAnalyzerError):
    """Raised when a required dependency is missing or incompatible."""
    def __init__(self, message, dependency=None):
        super().__init__(message)
        self.dependency = dependency

class UIError(CVAnalyzerError):
    """Raised for UI-related errors."""
    def __init__(self, message):
        super().__init__(message)
