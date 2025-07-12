# Custom exceptions for key error scenarios in CV Analyzer.
# Only comment where context is helpful.

class CVAnalyzerError(Exception):
    """Base exception for all CV Analyzer errors."""
    pass

class ResumeParsingError(CVAnalyzerError):
    """Resume parsing failed (invalid format, unreadable, etc)."""
    def __init__(self, message, file_path=None):
        super().__init__(message)
        self.file_path = file_path

class ATSAnalysisError(CVAnalyzerError):
    """ATS compatibility analysis failed."""
    def __init__(self, message, platform=None):
        super().__init__(message)
        self.platform = platform

class KeywordMatchingError(CVAnalyzerError):
    """Keyword matching failed (NLP or logic error)."""
    def __init__(self, message, job_description=None):
        super().__init__(message)
        self.job_description = job_description

class FeedbackGenerationError(CVAnalyzerError):
    def __init__(self, message):
        super().__init__(message)

class DependencyValidationError(CVAnalyzerError):
    # Raised if a required dependency or model is missing
    def __init__(self, message, dependency=None):
        super().__init__(message)
        self.dependency = dependency

class UIError(CVAnalyzerError):
    def __init__(self, message):
        super().__init__(message)
