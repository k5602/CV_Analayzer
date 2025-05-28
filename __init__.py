"""
Package initialization for CV_Analyzer
"""

__version__ = '1.0.0'
__author__ = 'AI-Powered Resume/CV Analyzer'

# Import main components for easier access
from controllers.analyzer_controller import AnalyzerController
from models.resume_parser import ResumeParser
from models.ats_checker import ATSChecker
from models.keyword_matcher import KeywordMatcher
from models.feedback_generator import FeedbackGenerator