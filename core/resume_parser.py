
from typing import Dict, Any
from loguru import logger
from core.resume_file_loader import ResumeFileLoader
from core.resume_text_extractor import ResumeTextExtractor
from core.resume_entity_extractor import ResumeEntityExtractor

class ResumeParser:
    def __init__(self):
        self.file_loader = ResumeFileLoader()
        self.text_extractor = ResumeTextExtractor()
        self.entity_extractor = ResumeEntityExtractor()

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        logger.info(f"Parsing resume: {file_path}")
        is_valid, error_message = self.file_loader.validate_file(file_path)
        if not is_valid:
            return {"error": error_message}

        extension = self.file_loader.get_file_extension(file_path)
        text = self.text_extractor.extract_text(file_path, extension)
        if not text:
            return {"error": "Could not extract text from resume."}

        entities = self.entity_extractor.extract_entities(text)
        entities["full_text"] = text
        return entities
