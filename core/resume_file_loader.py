"""
resume_file_loader.py
Handles loading resume files and basic file type validation.
Refactored out of ResumeParser for single-responsibility.
"""

import os
from typing import Optional, Tuple
from loguru import logger

class ResumeFileLoader:
    """
    Loads resume files and validates file types.
    Supports PDF, DOCX, and TXT formats.
    """

    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

    def __init__(self):
        pass

    def validate_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that the file exists and is a supported format.

        Args:
            file_path: Path to the resume file.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False, "File not found"

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported file format: {ext}")
            return False, f"Unsupported file format: {ext}. Please use PDF, DOCX, or TXT files."

        return True, None

    def get_file_extension(self, file_path: str) -> str:
        """
        Get the file extension for the given path.

        Args:
            file_path: Path to the file.

        Returns:
            File extension as a string (e.g., '.pdf')
        """
        return os.path.splitext(file_path)[1].lower()

    def load_file(self, file_path: str) -> Optional[bytes]:
        """
        Load the file contents as bytes.

        Args:
            file_path: Path to the file.

        Returns:
            File contents as bytes, or None if error.
        """
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            logger.info(f"Loaded file: {file_path} ({len(data)} bytes)")
            return data
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return None
