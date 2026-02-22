"""
Coursera Certificate Recommendation Service
Suggests relevant Coursera certificates based on user's study topics and weak points
"""
from .models import WeakPoint, CourseRecommendation
import time


class CourseraService:
    """Service to fetch and recommend Coursera certificates"""
    
    BASE_URL = "https://www.coursera.org"
    
    # Curated Coursera certificate programs by topic
    CERTIFICATE_MAP = {
        'python': [
            {
                'title': 'Python for Everybody Specialization',
                'url': 'https://www.coursera.org/specializations/python',
                'provider': 'University of Michigan',
                'description': 'Learn to Program and Analyze Data with Python',
                'duration': '8 months',
                'level': 'Beginner'
            },
            {
                'title': 'Python 3 Programming Specialization',
                'url': 'https://www.coursera.org/specializations/python-3-programming',
                'provider': 'University of Michigan',
                'description': 'A Comprehensive Introduction to Python 3',
                'duration': '5 months',
                'level': 'Beginner'
            }
        ],
        'machine learning': [
            {
                'title': 'Machine Learning Specialization',
                'url': 'https://www.coursera.org/specializations/machine-learning-introduction',
                'provider': 'Stanford University & DeepLearning.AI',
                'description': 'Master fundamental AI concepts and develop practical machine learning skills',
                'duration': '3 months',
                'level': 'Beginner'
            },
            {
                'title': 'Deep Learning Specialization',
                'url': 'https://www.coursera.org/specializations/deep-learning',
                'provider': 'DeepLearning.AI',
                'description': 'Build and train neural network architectures',
                'duration': '5 months',
                'level': 'Intermediate'
            }
        ],
        'data science': [
            {
                'title': 'IBM Data Science Professional Certificate',
                'url': 'https://www.coursera.org/professional-certificates/ibm-data-science',
                'provider': 'IBM',
                'description': 'Launch your career in Data Science',
                'duration': '11 months',
                'level': 'Beginner'
            },
            {
                'title': 'Google Data Analytics Professional Certificate',
                'url': 'https://www.coursera.org/professional-certificates/google-data-analytics',
                'provider': 'Google',
                'description': 'Get job-ready for an entry-level data analyst role',
                'duration': '6 months',
                'level': 'Beginner'
            }
        ],
        'web development': [
            {
                'title': 'Meta Front-End Developer Professional Certificate',
                'url': 'https://www.coursera.org/professional-certificates/meta-front-end-developer',
                'provider': 'Meta',
                'description': 'Launch your career as a front-end developer',
                'duration': '7 months',
                'level': 'Beginner'
            },
            {
                'title': 'IBM Full Stack Software Developer Professional Certificate',
                'url': 'https://www.coursera.org/professional-certificates/ibm-full-stack-cloud-developer',
                'provider': 'IBM',
                'description': 'Become job-ready for a career in full stack development',
                'duration': '12 months',
                'level': 'Beginner'
            }
        ],
        'javascript': [
            {
                'title': 'Meta Front-End Developer Professional Certificate',
                'url': 'https://www.coursera.org/professional-certificates/meta-front-end-developer',
                'provider': 'Meta',
                'description': 'Master JavaScript, React, and modern web development',
                'duration': '7 months',
                'level': 'Beginner'
            }
        ],
        'java': [
            {
                'title': 'Object Oriented Programming in Java Specialization',
                'url': 'https://www.coursera.org/specializations/object-oriented-programming',
                'provider': 'Duke University',
                'description': 'Learn to Think Like a Computer Scientist',
                'duration': '6 months',
                'level': 'Intermediate'
            }
        ],
        'cloud computing': [
            {
                'title': 'Google Cloud Professional Certificate',
                'url': 'https://www.coursera.org/professional-certificates/cloud-engineering-gcp',
                'provider': 'Google Cloud',
                'description': 'Prepare for a career in cloud engineering',
                'duration': '6 months',
                'level': 'Beginner'
            },
            {
                'title': 'AWS Fundamentals Specialization',
                'url': 'https://www.coursera.org/specializations/aws-fundamentals',
                'provider': 'Amazon Web Services',
                'description': 'Learn the fundamentals of AWS cloud',
                'duration': '4 months',
                'level': 'Beginner'
            }
        ],
        'cybersecurity': [
            {
                'title': 'Google Cybersecurity Professional Certificate',
                'url': 'https://www.coursera.org/professional-certificates/google-cybersecurity',
                'provider': 'Google',
                'description': 'Get job-ready for a career in cybersecurity',
                'duration': '6 months',
                'level': 'Beginner'
            }
        ],
        'ai': [
            {
                'title': 'AI For Everyone',
                'url': 'https://www.coursera.org/learn/ai-for-everyone',
                'provider': 'DeepLearning.AI',
                'description': 'Master the fundamentals of AI',
                'duration': '4 weeks',
                'level': 'Beginner'
            },
            {
                'title': 'IBM AI Engineering Professional Certificate',
                'url': 'https://www.coursera.org/professional-certificates/ai-engineer',
                'provider': 'IBM',
                'description': 'Master AI and Machine Learning',
                'duration': '12 months',
                'level': 'Intermediate'
            }
        ]
    }
    
    @staticmethod
    def find_matching_certificates(topic):
        """
        Find Coursera certificates matching a topic
        
        Args:
            topic: Topic string to match
        
        Returns:
            List of certificate dictionaries
        """
        topic_lower = topic.lower()
        
        # Direct match
        if topic_lower in CourseraService.CERTIFICATE_MAP:
            return CourseraService.CERTIFICATE_MAP[topic_lower]
        
        # Partial match
        for key, certificates in CourseraService.CERTIFICATE_MAP.items():
            if key in topic_lower or topic_lower in key:
                return certificates
        
        # Default recommendations
        return CourseraService.CERTIFICATE_MAP.get('python', [])
    
    @staticmethod
    def get_recommendations_for_user(user):
        """
        Get Coursera certificate recommendations based on user's recent study topics
        
        Args:
            user: User instance
        
        Returns:
            List of certificate recommendations
        """
        from .models import Topic
        
        # Get user's recent topics
        recent_topics = Topic.objects.filter(user=user).order_by('-updated_at')[:5]
        
        all_certificates = []
        seen_urls = set()
        
        for topic in recent_topics:
            certificates = CourseraService.find_matching_certificates(topic.name)
            
            for cert in certificates:
                if cert['url'] not in seen_urls:
                    seen_urls.add(cert['url'])
                    all_certificates.append({
                        **cert,
                        'related_topic': topic.name,
                        'relevance_score': 0.9
                    })
        
        return all_certificates[:10]  # Return top 10
    
    @staticmethod
    def get_recommendations_for_weak_points(user):
        """
        Get Coursera certificates for user's weak points
        
        Args:
            user: User instance
        
        Returns:
            List of certificate recommendations
        """
        weak_points = WeakPoint.objects.filter(
            user=user,
            confidence_score__lt=0.7
        ).order_by('confidence_score')[:5]
        
        all_certificates = []
        seen_urls = set()
        
        for wp in weak_points:
            certificates = CourseraService.find_matching_certificates(wp.topic)
            
            for cert in certificates:
                if cert['url'] not in seen_urls:
                    seen_urls.add(cert['url'])
                    all_certificates.append({
                        **cert,
                        'related_weak_point': wp.topic,
                        'weak_point_accuracy': wp.accuracy,
                        'relevance_score': 1.0 - wp.confidence_score  # Higher for weaker areas
                    })
        
        # Sort by relevance
        all_certificates.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return all_certificates[:10]
