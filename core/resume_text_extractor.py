"""
resume_text_extractor.py
Handles extraction of text content from resume files (PDF, DOCX, TXT).
Refactored out of ResumeParser for single-responsibility.
"""

import pdfplumber
import PyPDF2
import docx
from typing import Optional
from loguru import logger

class ResumeTextExtractor:
    """
    Extracts text from resume files in supported formats.
    Supports PDF, DOCX, and TXT.
    """

    def __init__(self, use_ocr: bool = False, ocr_func: Optional[callable] = None):
        """
        Args:
            use_ocr: Whether to use OCR for image-based PDFs.
            ocr_func: Optional OCR function for image-based PDFs.
        """
        self.use_ocr = use_ocr
        self.ocr_func = ocr_func

    def extract_text(self, file_path: str, extension: str) -> str:
        """
        Extract text from the given resume file.

        Args:
            file_path: Path to the resume file.
            extension: File extension (e.g., '.pdf', '.docx', '.txt').

        Returns:
            Extracted text as a string.
        """
        if extension == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif extension == '.docx':
            return self._extract_text_from_docx(file_path)
        elif extension == '.txt':
            return self._extract_text_from_txt(file_path)
        else:
            logger.error(f"Unsupported file extension for text extraction: {extension}")
            return ""

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        Uses pdfplumber first, then falls back to PyPDF2.
        If text is suspiciously short, attempts OCR if enabled.
        """
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed, trying PyPDF2: {e}")
            try:
                with open(pdf_path, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(reader.pages)):
                        page = reader.pages[page_num]
                        page_text = page.extract_text() or ""
                        text += page_text + "\n"
            except Exception as e2:
                logger.error(f"PyPDF2 extraction also failed: {e2}")

        # If text is suspiciously short, try OCR if available
        if self.use_ocr and len(text.strip()) < 100 and self.ocr_func:
            logger.info("PDF appears to be image-based, attempting OCR extraction")
            try:
                ocr_text = self.ocr_func(pdf_path)
                if ocr_text:
                    text += "\n" + ocr_text
            except Exception as ocr_e:
                logger.error(f"OCR extraction failed: {ocr_e}")

        return text

    def _extract_text_from_docx(self, docx_path: str) -> str:
        """
        Extract text content from a DOCX file.
        """
        text = ""
        try:
            doc = docx.Document(docx_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
        return text

    def _extract_text_from_txt(self, txt_path: str) -> str:
        """
        Extract text content from a TXT file.
        """
        text = ""
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
        return text
