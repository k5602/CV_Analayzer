"""
KeywordExtractor: Extracts keywords from text for resume/job description analysis.
Refactored out of KeywordMatcher for single-responsibility.
"""

import re
from typing import List, Set

class KeywordExtractor:
    """
    Extracts important keywords from text using regex, stopword filtering,
    and common technical term matching.
    """

    def __init__(self):
        # Define stop words for filtering
        self.stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
            'when', 'where', 'how', 'all', 'any', 'both', 'each', 'other', 'such',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will',
            'just', 'don', "don't", 'should', "should've", 'now', 'not', 'no',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'having', 'with', 'for', 'on', 'at',
            'by', 'from', 'up', 'down', 'in', 'out', 'over', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'why', 'how', 'all',
            'any', 'both', 'each', 'other', 'such', 'own', 'same', 'so', 'than',
            'too', 'very', 'can', 'will', 'just', 'don', "don't", 'should',
            "should've", 'now', 'not', 'no'
        }

        # Common technical terms and multi-word phrases
        self.common_skills = [
            # Programming languages
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go',
            'typescript', 'scala', 'r', 'perl', 'rust', 'dart', 'html', 'css', 'sql',

            # Frameworks and libraries
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js', 'express',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'keras', '.net', 'laravel',

            # Cloud & DevOps
            'aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible',
            'ci/cd', 'devops', 'microservices', 'serverless',

            # Databases
            'mysql', 'postgresql', 'mongodb', 'oracle', 'sql server', 'sqlite', 'redis', 'cassandra',
            'dynamodb', 'firebase',

            # Tools & Software
            'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack', 'trello',
            'visual studio code', 'intellij', 'eclipse', 'photoshop', 'illustrator', 'figma',

            # Soft skills
            'leadership', 'communication', 'teamwork', 'problem-solving', 'critical thinking',
            'time management', 'creativity', 'adaptability', 'project management', 'agile',
            'scrum', 'kanban',

            # Data science/AI
            'machine learning', 'deep learning', 'artificial intelligence', 'data science',
            'data analysis', 'natural language processing', 'computer vision', 'big data',
            'data engineering', 'data visualization', 'statistics', 'analytics',

            # Mobile development
            'ios', 'android', 'react native', 'flutter', 'mobile development', 'app development',
            'cross-platform', 'pwa',

            # Other technical skills
            'rest api', 'graphql', 'oauth', 'jwt', 'web services', 'soa', 'mvc', 'orm',
            'responsive design', 'web accessibility', 'ui/ux', 'frontend', 'backend',
            'full-stack', 'testing', 'qa', 'security', 'blockchain'
        ]

    def extract_keywords(self, text: str) -> Set[str]:
        """
        Extract important keywords from text.

        Args:
            text: Input text to extract keywords from

        Returns:
            Set of extracted keywords
        """
        text = text.lower()

        # Extract words (alphanumeric sequences) that are not in stop words
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#\-.]*[a-zA-Z0-9]\b', text)
        filtered_words = [w for w in words if w not in self.stop_words and len(w) > 2]

        # Extract common technical terms and multi-word phrases
        skill_matches = set()
        for skill in self.common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text):
                skill_matches.add(skill)

        # Combine single words and skill phrases
        keywords = set(filtered_words) | skill_matches
        return keywords

    def extract_key_requirements(self, job_description: str, num_requirements: int = 10) -> List[str]:
        """
        Extract key requirements from a job description using TF-IDF or simple frequency.

        Args:
            job_description: Job description text
            num_requirements: Number of key requirements to extract

        Returns:
            List of key requirement phrases
        """
        # Simple frequency-based extraction for environments without KeyBERT
        text = job_description.lower()
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#\-.]*[a-zA-Z0-9]\b', text)
        filtered_words = [w for w in words if w not in self.stop_words and len(w) > 2]

        # Count frequencies
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and select top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [word for word, freq in sorted_words[:num_requirements]]

        # Add common skills found in the job description
        skill_matches = []
        for skill in self.common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text):
                skill_matches.append(skill)

        # Combine and deduplicate
        requirements = list(dict.fromkeys(top_keywords + skill_matches))
        return requirements[:num_requirements]
