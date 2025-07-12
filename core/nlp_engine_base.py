from abc import ABC, abstractmethod
from typing import List, Dict, Any

class NLPEngineBase(ABC):
    """
    Abstract base class for pluggable NLP engines.
    Implementations should provide methods for entity extraction, keyword extraction,
    noun phrase detection, and semantic similarity calculation.
    """

    @abstractmethod
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from the given text.
        Returns a list of dictionaries with entity type and value.
        """
        pass

    @abstractmethod
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract top N keywords from the given text.
        Returns a list of keywords.
        """
        pass

    @abstractmethod
    def get_noun_phrases(self, text: str) -> List[str]:
        """
        Extract noun phrases from the given text.
        Returns a list of noun phrases.
        """
        pass

    @abstractmethod
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        Returns a float score between 0 and 1.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the NLP engine and its dependencies are available.
        Returns True if available, False otherwise.
        """
        pass
