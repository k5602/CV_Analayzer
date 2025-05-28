import re
from typing import Dict, List, Set, Tuple, Optional, Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from loguru import logger

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence_transformers not available, falling back to TF-IDF")

class KeywordMatcher:
    """
    A class for matching keywords between a resume and job description
    and calculating similarity scores using NLP techniques.
    """

    def __init__(self, use_transformer: bool = True):
        """
        Initialize the KeywordMatcher with desired similarity model.
        
        Args:
            use_transformer: Whether to use transformer models (more accurate but slower) or TF-IDF
        """
        self.use_transformer = use_transformer and SENTENCE_TRANSFORMERS_AVAILABLE
        self.transformer_model = None
        self.tfidf_vectorizer = None
        
        try:
            if self.use_transformer:
                logger.info("Loading sentence transformer model...")
                self.transformer_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
                logger.success("Sentence transformer model loaded successfully")
            else:
                logger.info("Initializing TF-IDF vectorizer...")
                self.tfidf_vectorizer = TfidfVectorizer(
                    stop_words='english',
                    ngram_range=(1, 2),  # Consider single words and bigrams
                    max_features=10000
                )
                logger.success("TF-IDF vectorizer initialized")
        except Exception as e:
            logger.error(f"Error initializing keyword matching models: {e}")
            # Fall back to TF-IDF if transformer fails
            self.use_transformer = False
            self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
            
    def match_keywords(self, resume_text: str, job_description: str) -> Dict:
        """
        Match keywords between resume and job description, calculating similarity scores.
        
        Args:
            resume_text: Full text of the resume
            job_description: Full text of the job description
            
        Returns:
            Dictionary containing match results including similarity scores and keyword matches
        """
        try:
            # Extract keywords from both texts
            job_keywords = self.extract_keywords(job_description)
            resume_keywords = self.extract_keywords(resume_text)
            
            # Find common and missing keywords
            common_keywords = resume_keywords.intersection(job_keywords)
            missing_keywords = job_keywords - resume_keywords
            
            # Calculate semantic similarity
            semantic_similarity = self._calculate_semantic_similarity(resume_text, job_description)
            
            # Calculate keyword match ratio
            match_ratio = len(common_keywords) / max(1, len(job_keywords)) * 100
            
            # Calculate skill match percentage (combination of semantic and keyword matching)
            # We weight semantic similarity higher as it captures meaning beyond exact matches
            skill_match = 0.7 * semantic_similarity + 0.3 * match_ratio
            
            result = {
                "skill_match_percentage": round(skill_match),
                "semantic_similarity": round(semantic_similarity, 2),
                "keyword_match_ratio": round(match_ratio, 2),
                "matching_keywords": sorted(list(common_keywords)),
                "missing_keywords": sorted(list(missing_keywords)),
                "resume_unique_keywords": sorted(list(resume_keywords - job_keywords))
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in keyword matching: {e}")
            return {
                "error": f"Error in keyword matching: {str(e)}",
                "skill_match_percentage": 0,
                "matching_keywords": [],
                "missing_keywords": []
            }
    
    def extract_keywords(self, text: str) -> Set[str]:
        """
        Extract important keywords from text.
        
        Args:
            text: Input text to extract keywords from
            
        Returns:
            Set of extracted keywords
        """
        # Convert to lowercase
        text = text.lower()
        
        # Define stop words for filtering
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
            'when', 'where', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just',
            'don', 'should', 'now', 'to', 'from', 'with', 'for', 'by', 'about',
            'against', 'between', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
            'under', 'again', 'further', 'then', 'once', 'here', 'there', 'why',
            'this', 'that', 'these', 'those', 'i', 'me', 'my', 'myself', 'we',
            'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
            "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
            'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it',
            "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs',
            'themselves', 'who', 'whom', 'am', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
            'doing', 'would', 'should', 'could', 'ought', "i'm", "i've", "i'll",
            "i'd", "we're", "we've", "we'll", "we'd", "he's", "he'd", "she'll",
            "she'd", "it'll", "they're", "they've", "they'll", "they'd", "isn't",
            "aren't", "wasn't", "weren't", "hasn't", "haven't", "hadn't", "doesn't",
            "don't", "didn't", "won't", "wouldn't", "shan't", "shouldn't", "can't",
            "cannot", "couldn't", "mustn't", "let's", "that's", "there's"
        }
        
        # Extract words (alphanumeric sequences) that are not in stop words
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#\-.]*[a-zA-Z0-9]\b', text)
        filtered_words = [w for w in words if w.lower() not in stop_words and len(w) > 2]
        
        # Extract common technical terms and multi-word phrases
        common_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'sql', 'nosql',
            'aws', 'azure', 'cloud', 'docker', 'kubernetes', 'ci/cd', 'devops', 'machine learning',
            'data science', 'data analysis', 'artificial intelligence', 'deep learning',
            'project management', 'agile', 'scrum', 'team lead', 'leadership', 'communication',
            'problem solving', 'critical thinking', 'collaboration', 'customer service',
            'database', 'front-end', 'back-end', 'full-stack', 'testing', 'qa', 'ux', 'ui',
            'product management', 'mobile development', 'android', 'ios', 'react native',
            'flask', 'django', 'spring boot', 'mongodb', 'postgresql', 'mysql', 'git',
            'linux', 'unix', 'networking', 'security', 'api', 'rest', 'graphql', 'html', 'css',
            'sass', 'less', 'typescript', 'golang', 'rust', 'c++', 'c#', '.net', 'ruby',
            'php', 'laravel', 'symfony', 'wordpress', 'drupal', 'joomla', 'magento',
            'shopify', 'woocommerce', 'e-commerce', 'seo', 'sem', 'digital marketing',
            'content marketing', 'social media', 'email marketing', 'crm', 'salesforce',
            'hubspot', 'marketo', 'adobe', 'photoshop', 'illustrator', 'indesign',
            'after effects', 'premiere pro', 'figma', 'sketch', 'invision', 'wireframing',
            'prototyping', 'responsive design', 'mobile first', 'web design',
            'graphic design', 'user research', 'data visualization', 'tableau', 'power bi',
            'excel', 'vba', 'microsoft office', 'accounting', 'finance', 'analytics',
            'reporting', 'blockchain', 'cryptocurrency', 'smart contracts', 'solidity',
            'ethereum', 'information security', 'cyber security', 'penetration testing',
            'vulnerability assessment', 'risk management', 'compliance', 'gdpr',
            'hipaa', 'sox', 'iso27001', 'itil', 'service management', 'operations',
            'supply chain', 'logistics', 'inventory management', 'procurement',
            'negotiation', 'vendor management', 'relationship management',
            'stakeholder management', 'team building', 'mentoring', 'coaching',
            'talent acquisition', 'recruitment', 'onboarding', 'training'
        ]
        
        skill_matches = set()
        text_lower = text.lower()
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                skill_matches.add(skill)
        
        # Combine single words and skill phrases
        keywords = set(filtered_words) | skill_matches
        
        return keywords
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two text documents.
        
        Args:
            text1: First text document
            text2: Second text document
            
        Returns:
            Similarity score between 0 and 100
        """
        if not text1 or not text2:
            return 0.0
            
        try:
            if self.use_transformer and self.transformer_model:
                # Use sentence transformers for semantic similarity (more accurate)
                embeddings1 = self.transformer_model.encode([text1])
                embeddings2 = self.transformer_model.encode([text2])
                
                # Calculate cosine similarity
                similarity = cosine_similarity(embeddings1, embeddings2)[0][0]
                
            else:
                # Fall back to TF-IDF for similarity calculation
                if not self.tfidf_vectorizer:
                    self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
                    
                vectorizer = self.tfidf_vectorizer
                try:
                    tfidf_matrix = vectorizer.fit_transform([text1, text2])
                    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                except:
                    # If vectorization fails (e.g., empty documents after preprocessing)
                    return 0.0
            
            # Convert similarity to percentage
            return similarity * 100
            
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return 0.0

    def extract_key_requirements(self, job_description: str, num_requirements: int = 10) -> List[str]:
        """
        Extract key requirements from a job description.
        
        Args:
            job_description: Job description text
            num_requirements: Number of key requirements to extract
            
        Returns:
            List of key requirement phrases
        """
        try:
            # Try to use KeyBERT if available
            try:
                from keybert import KeyBERT
                kw_model = KeyBERT()
                keywords = kw_model.extract_keywords(
                    job_description, 
                    keyphrase_ngram_range=(1, 3), 
                    stop_words='english', 
                    top_n=num_requirements
                )
                return [kw[0] for kw in keywords]
            except ImportError:
                logger.warning("KeyBERT not available, using simplified keyword extraction")
                
            # Simplified keyword extraction using TF-IDF
            vectorizer = TfidfVectorizer(
                ngram_range=(1, 3),
                stop_words='english',
                max_features=100
            )
            
            # Split text into sentences for better context
            sentences = re.split(r'[.!?]', job_description)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            
            if not sentences:
                return []
                
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get top TF-IDF scores for each sentence
            requirements = []
            for i, sentence in enumerate(sentences):
                if len(requirements) >= num_requirements:
                    break
                    
                # Get top features for this sentence
                feature_index = tfidf_matrix[i].indices
                feature_scores = zip(feature_index, [tfidf_matrix[i, x] for x in feature_index])
                feature_scores = sorted(feature_scores, key=lambda x: x[1], reverse=True)
                
                # Extract top features
                for idx, score in feature_scores[:3]:  # Get top 3 from each sentence
                    if len(requirements) >= num_requirements:
                        break
                    feature = feature_names[idx]
                    if feature not in requirements and len(feature.split()) <= 3:
                        requirements.append(feature)
            
            return requirements
            
        except Exception as e:
            logger.error(f"Error extracting key requirements: {e}")
            return []
                
    def analyze_skill_match(self, 
                          resume_data: Dict, 
                          job_description: str) -> Dict[str, Union[int, List[str]]]:
        """
        Comprehensive analysis of how well a resume matches a job description.
        
        Args:
            resume_data: Parsed resume data dictionary
            job_description: Job description text
            
        Returns:
            Dictionary with match analysis results
        """
        try:
            # Extract text from resume sections
            resume_text = resume_data.get("full_text", "")
            if not resume_text:
                resume_text = " ".join([
                    str(resume_data.get("summary", "")),
                    " ".join(str(exp.get("description", "")) for exp in resume_data.get("experience", [])),
                    " ".join(str(skill) for skill in resume_data.get("skills", [])),
                    " ".join(str(edu.get("description", "")) for edu in resume_data.get("education", [])),
                    " ".join(str(proj.get("description", "")) for proj in resume_data.get("projects", []))
                ])
            
            # Match keywords between resume and job description
            match_results = self.match_keywords(resume_text, job_description)
            
            # Extract key requirements from job description
            key_requirements = self.extract_key_requirements(job_description)
            
            # Calculate match percentages for different sections
            experience_text = " ".join(
                str(exp.get("title", "")) + " " + 
                str(exp.get("company", "")) + " " + 
                str(exp.get("description", ""))
                for exp in resume_data.get("experience", [])
            )
            experience_match = self._calculate_semantic_similarity(experience_text, job_description)
            
            education_text = " ".join(
                str(edu.get("degree", "")) + " " + 
                str(edu.get("institution", "")) + " " + 
                str(edu.get("description", ""))
                for edu in resume_data.get("education", [])
            )
            education_match = self._calculate_semantic_similarity(education_text, job_description)
            
            skills_text = " ".join(str(skill) for skill in resume_data.get("skills", []))
            skills_match = self._calculate_semantic_similarity(skills_text, job_description)
            
            # Calculate overall match score (weighted average)
            overall_match = round(
                0.45 * match_results.get("skill_match_percentage", 0) +  # Weight overall skill match highest
                0.25 * experience_match +  # Experience is next most important
                0.20 * skills_match +      # Explicit skills section
                0.10 * education_match     # Education typically least important for matching
            )
            
            # Identify strong matches and gaps
            strong_matches = match_results.get("matching_keywords", [])[:5]
            key_gaps = [req for req in key_requirements if req not in strong_matches][:5]
            
            result = {
                "overall_match_percentage": overall_match,
                "skill_match_percentage": match_results.get("skill_match_percentage", 0),
                "experience_match_percentage": round(experience_match),
                "education_match_percentage": round(education_match),
                "skills_match_percentage": round(skills_match),
                "key_requirements": key_requirements,
                "strong_matches": strong_matches,
                "key_gaps": key_gaps,
                "matching_keywords": match_results.get("matching_keywords", []),
                "missing_keywords": match_results.get("missing_keywords", []),
                "resume_unique_keywords": match_results.get("resume_unique_keywords", [])
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in skill match analysis: {e}")
            return {
                "error": f"Error in skill match analysis: {str(e)}",
                "overall_match_percentage": 0,
                "skill_match_percentage": 0,
                "experience_match_percentage": 0,
                "education_match_percentage": 0,
                "skills_match_percentage": 0,
            }