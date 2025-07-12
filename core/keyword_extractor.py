"""
KeywordExtractor: Extracts keywords from resume/job description text.
Only key logic is commented for clarity.
"""

import re
from typing import List, Set

class KeywordExtractor:
    """
    Extracts important keywords from text using regex, stopword filtering,
    and common technical term matching.
    """

    def __init__(self):
        # Stop words for keyword filtering
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

        # Common technical and soft skills for matching
        self.common_skills = [
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go',
            'typescript', 'scala', 'r', 'perl', 'rust', 'dart', 'html', 'css', 'sql',
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js', 'express',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'keras', '.net', 'laravel',
            'aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible',
            'ci/cd', 'devops', 'microservices', 'serverless',
            'mysql', 'postgresql', 'mongodb', 'oracle', 'sql server', 'sqlite', 'redis', 'cassandra',
            'dynamodb', 'firebase',
            'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack', 'trello',
            'visual studio code', 'intellij', 'eclipse', 'photoshop', 'illustrator', 'figma',
            'leadership', 'communication', 'teamwork', 'problem-solving', 'critical thinking',
            'time management', 'creativity', 'adaptability', 'project management', 'agile',
            'scrum', 'kanban',
            'machine learning', 'deep learning', 'artificial intelligence', 'data science',
            'data analysis', 'natural language processing', 'computer vision', 'big data',
            'data engineering', 'data visualization', 'statistics', 'analytics',
            'ios', 'android', 'react native', 'flutter', 'mobile development', 'app development',
            'cross-platform', 'pwa',
            'rest api', 'graphql', 'oauth', 'jwt', 'web services', 'soa', 'mvc', 'orm',
            'responsive design', 'web accessibility', 'ui/ux', 'frontend', 'backend',
            'full-stack', 'testing', 'qa', 'security', 'blockchain'
        ]

    def extract_keywords(self, text: str) -> Set[str]:
        """
        Extracts keywords using stopword filtering and skill matching.
        """
        text = text.lower()
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#\-.]*[a-zA-Z0-9]\b', text)
        filtered_words = [w for w in words if w not in self.stop_words and len(w) > 2]

        # Match known skills/technologies
        skill_matches = set()
        for skill in self.common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text):
                skill_matches.add(skill)

        keywords = set(filtered_words) | skill_matches
        return keywords

    def extract_key_requirements(self, job_description: str, num_requirements: int = 10) -> List[str]:
        """
        Returns top requirements from a job description (frequency + skill match).
        """
        text = job_description.lower()
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#\-.]*[a-zA-Z0-9]\b', text)
        filtered_words = [w for w in words if w not in self.stop_words and len(w) > 2]

        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [word for word, freq in sorted_words[:num_requirements]]

        skill_matches = []
        for skill in self.common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text):
                skill_matches.append(skill)

        requirements = list(dict.fromkeys(top_keywords + skill_matches))
        return requirements[:num_requirements]
