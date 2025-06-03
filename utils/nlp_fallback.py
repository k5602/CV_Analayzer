import re
import string
from typing import List, Dict, Set, Tuple, Optional, Any
import logging

# Configure logger
logger = logging.getLogger(__name__)

class SimplifiedNLPProcessor:
    """
    A basic NLP processor that provides simplified alternatives to spaCy functionality.
    This is used as a fallback when spaCy is not available.
    """
    
    def __init__(self):
        """Initialize the simplified NLP processor with basic resources."""
        self.stopwords = self._load_stopwords()
        self.common_names = self._load_common_names()
        self.locations = self._load_locations()
        
        # Define common part-of-speech categories based on heuristics
        self.noun_endings = ('tion', 'ment', 'ence', 'ance', 'ity', 'ness', 'ship', 'age', 'ery')
        self.adj_endings = ('able', 'ible', 'al', 'ful', 'ic', 'ive', 'less', 'ous')
        self.verb_endings = ('ate', 'ize', 'ise', 'ify', 'en', 'ed', 'ing')
        
    def _load_stopwords(self) -> Set[str]:
        """Load a basic set of English stopwords."""
        return {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
            'when', 'where', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just',
            'don', 'should', 'now', 'to', 'from', 'with', 'for', 'by', 'about',
            'against', 'between', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
            'under', 'again', 'further', 'then', 'once', 'here', 'there', 'why',
            'this', 'that', 'these', 'those', 'i', 'me', 'my', 'myself', 'we',
            'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
            'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it',
            'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
            'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'would', 'could',
            'should', 'shall', 'must', 'may', 'might', 'at'
        }
    
    def _load_common_names(self) -> Set[str]:
        """Load a small set of common names for entity detection."""
        return {
            'john', 'david', 'michael', 'james', 'robert', 'william', 'joseph', 'thomas',
            'mary', 'jennifer', 'lisa', 'sarah', 'michelle', 'patricia', 'elizabeth',
            'smith', 'johnson', 'williams', 'brown', 'jones', 'miller', 'davis', 
            'garcia', 'rodriguez', 'wilson', 'martinez', 'anderson', 'taylor', 'lee'
        }
    
    def _load_locations(self) -> Set[str]:
        """Load a small set of common locations for entity detection."""
        return {
            'new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia',
            'san antonio', 'san diego', 'dallas', 'san jose', 'austin', 'boston', 
            'seattle', 'toronto', 'london', 'paris', 'berlin', 'sydney', 'tokyo',
            'beijing', 'mumbai', 'delhi', 'singapore', 'dubai', 'usa', 'canada', 
            'uk', 'england', 'france', 'germany', 'australia', 'india', 'china', 'japan'
        }
    
    def preprocess_text(self, text: str) -> str:
        """
        Basic text preprocessing: lowercase, remove punctuation, extra whitespace.
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Simple word tokenization.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens
        """
        # Preprocess text
        text = self.preprocess_text(text)
        
        # Split into words
        tokens = text.split()
        
        return tokens
    
    def extract_keywords(self, text: str, n: int = 10) -> List[str]:
        """
        Extract keywords from text using simple frequency analysis.
        
        Args:
            text: Input text
            n: Maximum number of keywords to return
            
        Returns:
            List of keywords
        """
        # Tokenize and convert to lowercase
        tokens = [word.lower() for word in self.tokenize(text)]
        
        # Remove stopwords and very short words
        filtered_tokens = [word for word in tokens 
                          if word not in self.stopwords and len(word) > 2]
        
        # Count word frequencies
        word_freq = {}
        for word in filtered_tokens:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency (descending)
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top n keywords
        return [word for word, freq in sorted_words[:n]]
    
    def extract_bigrams(self, text: str, n: int = 10) -> List[str]:
        """
        Extract bigrams (two-word phrases) from text.
        
        Args:
            text: Input text
            n: Maximum number of bigrams to return
            
        Returns:
            List of bigram phrases
        """
        # Tokenize
        tokens = self.tokenize(text)
        
        # Create bigrams
        bigrams = []
        for i in range(len(tokens) - 1):
            if tokens[i] not in self.stopwords and tokens[i+1] not in self.stopwords:
                if len(tokens[i]) > 2 and len(tokens[i+1]) > 2:  # Skip very short words
                    bigram = f"{tokens[i]} {tokens[i+1]}"
                    bigrams.append(bigram)
        
        # Count frequencies
        bigram_freq = {}
        for bigram in bigrams:
            bigram_freq[bigram] = bigram_freq.get(bigram, 0) + 1
        
        # Sort by frequency (descending)
        sorted_bigrams = sorted(bigram_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top n bigrams
        return [bigram for bigram, freq in sorted_bigrams[:n]]
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities using simple heuristics.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with entity types and lists of entities
        """
        entities = {
            "PERSON": [],
            "LOCATION": [],
            "ORG": [],
            "SKILL": []
        }
        
        # Tokenize while preserving case
        words = text.split()
        
        # Extract potential named entities (capitalized words not at start of sentence)
        potential_entities = []
        for i, word in enumerate(words):
            # Check if word is capitalized and not at sentence start
            if (word and word[0].isupper() and
                (i > 0 and words[i-1][-1] not in '.!?')):
                potential_entities.append(word.strip('.,;:()[]{}'))
        
        # Process potential entities
        for entity in potential_entities:
            entity_lower = entity.lower()
            
            # Skip stopwords and short words
            if entity_lower in self.stopwords or len(entity_lower) < 3:
                continue
            
            # Check for person names
            if entity_lower in self.common_names:
                if entity not in entities["PERSON"]:
                    entities["PERSON"].append(entity)
            
            # Check for locations
            elif entity_lower in self.locations:
                if entity not in entities["LOCATION"]:
                    entities["LOCATION"].append(entity)
            
            # Check for organizations (heuristic: uppercase acronyms or ends with common suffixes)
            elif (entity.isupper() and len(entity) >= 2) or \
                 any(entity_lower.endswith(suffix) for suffix in ('inc', 'corp', 'llc', 'ltd')):
                if entity not in entities["ORG"]:
                    entities["ORG"].append(entity)
        
        # Also check for location bigrams
        for location in self.locations:
            if ' ' in location and location.lower() in text.lower():
                # Get the proper case from the text
                location_pattern = re.compile(re.escape(location), re.IGNORECASE)
                match = location_pattern.search(text)
                if match:
                    proper_case = match.group(0)
                    if proper_case not in entities["LOCATION"]:
                        entities["LOCATION"].append(proper_case)
        
        return entities
    
    def get_noun_phrases(self, text: str) -> List[str]:
        """
        Extract probable noun phrases using simple heuristics.
        
        Args:
            text: Input text
            
        Returns:
            List of noun phrases
        """
        # Tokenize but preserve case and punctuation
        tokens = re.findall(r'\b\w+\b', text)
        
        # Find potential noun phrases (adjective + noun combinations)
        noun_phrases = []
        for i in range(len(tokens) - 1):
            # Skip if either word is a stopword
            if tokens[i].lower() in self.stopwords or tokens[i+1].lower() in self.stopwords:
                continue
                
            # Is the second word likely a noun?
            second_is_noun = (
                tokens[i+1].lower().endswith(self.noun_endings) or
                not any(tokens[i+1].lower().endswith(ending) for ending in 
                        self.adj_endings + self.verb_endings)
            )
            
            # Is the first word likely an adjective?
            first_is_adj = tokens[i].lower().endswith(self.adj_endings)
            
            # Check if we have an adjective + noun pattern
            if (first_is_adj and second_is_noun) or second_is_noun:
                if len(tokens[i]) > 1 and len(tokens[i+1]) > 1:  # Skip very short words
                    phrase = f"{tokens[i]} {tokens[i+1]}"
                    noun_phrases.append(phrase)
        
        return noun_phrases
    
    def detect_skills(self, text: str, skills_db: Set[str]) -> List[str]:
        """
        Detect skills mentioned in the text using a skills database.
        
        Args:
            text: Input text
            skills_db: Set of skill keywords to match
            
        Returns:
            List of skills found in the text
        """
        text_lower = text.lower()
        found_skills = []
        
        for skill in skills_db:
            # Use word boundaries to match whole words only
            skill_pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(skill_pattern, text_lower):
                found_skills.append(skill)
        
        return found_skills
    
    def extract_dates(self, text: str) -> List[str]:
        """
        Extract date expressions from text using regex patterns.
        
        Args:
            text: Input text
            
        Returns:
            List of date expressions
        """
        patterns = [
            # Month Year - Month Year (Jan 2020 - Dec 2021)
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}\s*(-|–|to)\s*'
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}',
            
            # MM/YYYY - MM/YYYY (05/2020 - 06/2021)
            r'\d{1,2}/\d{4}\s*(-|–|to)\s*\d{1,2}/\d{4}',
            
            # YYYY - YYYY (2020 - 2021)
            r'\d{4}\s*(-|–|to)\s*\d{4}',
            
            # YYYY - Present (2020 - Present)
            r'\d{4}\s*(-|–|to)\s*(present|current|now)',
            
            # Month Year - Present
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}\s*(-|–|to)\s*'
            r'(present|current|now)'
        ]
        
        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if isinstance(matches, list) and matches:
                if all(isinstance(match, tuple) for match in matches):
                    # If matches are tuples (from captured groups), convert to strings
                    for match_groups in matches:
                        # Try to reconstruct the full match
                        if match_groups:
                            date_str = ''
                            for group in match_groups:
                                if group and isinstance(group, str):
                                    date_str += group + ' '
                            if date_str.strip():
                                dates.append(date_str.strip())
                else:
                    # If matches are strings, add them directly
                    dates.extend([m for m in matches if m])
                    
        return dates
    
    def cosine_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simplified cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        # Tokenize and filter stopwords
        tokens1 = [w for w in self.tokenize(text1) if w not in self.stopwords]
        tokens2 = [w for w in self.tokenize(text2) if w not in self.stopwords]
        
        # Create sets of unique tokens
        unique1 = set(tokens1)
        unique2 = set(tokens2)
        
        # Calculate intersection and union
        intersection = unique1.intersection(unique2)
        
        # If either set is empty, similarity is 0
        if not unique1 or not unique2:
            return 0.0
        
        # Calculate Jaccard similarity (intersection over union)
        jaccard = len(intersection) / (len(unique1) + len(unique2) - len(intersection))
        
        # Use frequency information to weight the similarity
        weighted_sim = 0.0
        token1_freq = {t: tokens1.count(t) for t in unique1}
        token2_freq = {t: tokens2.count(t) for t in unique2}
        
        # Sum of product of frequencies
        for token in intersection:
            weighted_sim += token1_freq[token] * token2_freq[token]
            
        # Normalize by total frequencies
        total1 = sum(token1_freq.values())
        total2 = sum(token2_freq.values())
        
        if total1 > 0 and total2 > 0:
            # Blend jaccard and weighted similarity
            return 0.6 * jaccard + 0.4 * (weighted_sim / (total1 * total2))
        else:
            return jaccard


class NLPFacade:
    """
    A facade class that provides consistent NLP functionality regardless of 
    whether spaCy is available or not.
    """
    
    def __init__(self):
        """Initialize the NLP facade with appropriate implementation."""
        self._impl = None
        self._is_spacy = False
        
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            self._is_spacy = True
            logger.info("Using spaCy for NLP processing")
        except Exception as e:
            self._impl = SimplifiedNLPProcessor()
            logger.warning(f"spaCy not available, using simplified NLP: {e}")
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        if self._is_spacy:
            try:
                doc = self.nlp(text)
                entities = {"PERSON": [], "LOC": [], "ORG": [], "GPE": []}
                
                for ent in doc.ents:
                    if ent.label_ in entities:
                        entities[ent.label_].append(ent.text)
                
                return entities
            except Exception as e:
                logger.warning(f"Error in spaCy entity extraction, falling back to simplified: {e}")
                return self._impl.extract_entities(text)
        else:
            return self._impl.extract_entities(text)
    
    def extract_keywords(self, text: str, n: int = 10) -> List[str]:
        """Extract keywords from text."""
        if self._is_spacy:
            try:
                doc = self.nlp(text)
                # Get tokens that are not stopwords or punctuation
                keywords = [token.text.lower() for token in doc 
                          if not token.is_stop and not token.is_punct and token.has_vector]
                
                # Count frequencies
                from collections import Counter
                keyword_freq = Counter(keywords)
                
                # Return most common keywords
                return [kw for kw, _ in keyword_freq.most_common(n)]
            except Exception as e:
                logger.warning(f"Error in spaCy keyword extraction, falling back to simplified: {e}")
                return self._impl.extract_keywords(text, n)
        else:
            return self._impl.extract_keywords(text, n)
    
    def get_noun_phrases(self, text: str) -> List[str]:
        """Extract noun phrases from text."""
        if self._is_spacy:
            try:
                doc = self.nlp(text)
                return [chunk.text for chunk in doc.noun_chunks]
            except Exception as e:
                logger.warning(f"Error in spaCy noun phrase extraction, falling back to simplified: {e}")
                return self._impl.get_noun_phrases(text)
        else:
            return self._impl.get_noun_phrases(text)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        if self._is_spacy:
            try:
                doc1 = self.nlp(text1)
                doc2 = self.nlp(text2)
                
                if not doc1.vector_norm or not doc2.vector_norm:
                    # If one of the docs couldn't be vectorized properly
                    return self._impl.cosine_similarity(text1, text2)
                    
                return doc1.similarity(doc2)
            except Exception as e:
                logger.warning(f"Error in spaCy similarity calculation, falling back to simplified: {e}")
                return self._impl.cosine_similarity(text1, text2)
        else:
            return self._impl.cosine_similarity(text1, text2)
    
    def is_using_spacy(self) -> bool:
        """Check if spaCy is being used."""
        return self._is_spacy

# Create a singleton instance for easy import
nlp = NLPFacade()