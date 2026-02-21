"""
Course Recommendation Service - Integrate with WebScrappingModule
"""
import sys
import os
import json
from pathlib import Path
from .models import WeakPoint, CourseRecommendation


class RecommendationService:
    """Generate course recommendations based on weak points"""
    
    @staticmethod
    def generate_recommendations(weak_point):
        """
        Generate recommendations for a weak point using web scraper
        
        Args:
            weak_point: WeakPoint instance
        
        Returns:
            dict with recommendations
        """
        topic = weak_point.topic
        
        # Try to use the scraper
        try:
            recommendations = RecommendationService._scrape_content(topic)
        except Exception as e:
            print(f"Scraper error: {e}")
            # Fallback to mock data
            recommendations = RecommendationService._get_fallback_recommendations(topic)
        
        # Store recommendations in database
        stored_count = 0
        
        # Store YouTube playlists
        for playlist in recommendations.get('playlists', [])[:5]:
            CourseRecommendation.objects.get_or_create(
                weak_point=weak_point,
                url=playlist['url'],
                defaults={
                    'user': weak_point.user,
                    'title': playlist['title'],
                    'source': 'youtube',
                    'description': f"By {playlist.get('channel', 'Unknown')}",
                    'relevance_score': 0.9
                }
            )
            stored_count += 1
        
        # Store articles
        for article in recommendations.get('articles', [])[:5]:
            CourseRecommendation.objects.get_or_create(
                weak_point=weak_point,
                url=article['url'],
                defaults={
                    'user': weak_point.user,
                    'title': article['title'],
                    'source': 'article',
                    'description': article.get('source', 'Web Article'),
                    'relevance_score': 0.8
                }
            )
            stored_count += 1
        
        # Store Q&A
        for question in recommendations.get('questions', [])[:3]:
            CourseRecommendation.objects.get_or_create(
                weak_point=weak_point,
                url=question['url'],
                defaults={
                    'user': weak_point.user,
                    'title': question['title'],
                    'source': 'stackoverflow',
                    'description': f"{question.get('votes', '0')} votes",
                    'relevance_score': 0.7
                }
            )
            stored_count += 1
        
        # Mark recommendations as generated
        weak_point.recommendations_generated = True
        weak_point.save()
        
        return {
            'success': True,
            'recommendations_count': stored_count,
            'playlists': len(recommendations.get('playlists', [])),
            'articles': len(recommendations.get('articles', [])),
            'questions': len(recommendations.get('questions', []))
        }
    
    @staticmethod
    def _scrape_content(topic):
        """
        Use WebScrappingModule to scrape content
        
        Args:
            topic: Topic to search for
        
        Returns:
            dict with scraped content
        """
        # Get path to scraper
        project_root = Path(__file__).parent.parent.parent
        scraper_path = project_root / 'WebScrappingModule' / 'Scripts'
        
        # Add to Python path
        if str(scraper_path) not in sys.path:
            sys.path.insert(0, str(scraper_path))
        
        try:
            # Import the latest scraper
            from selenium_scraper_2026 import AdaptiveContentScraper
            
            # Create scraper instance
            scraper = AdaptiveContentScraper()
            
            # Scrape content
            results = scraper.scrape_all(topic)
            
            # Close browser
            scraper.close()
            
            return results
            
        except ImportError as e:
            print(f"Could not import scraper: {e}")
            raise
        except Exception as e:
            print(f"Scraping error: {e}")
            raise
    
    @staticmethod
    def _get_fallback_recommendations(topic):
        """
        Fallback recommendations when scraper fails
        
        Args:
            topic: Topic to search for
        
        Returns:
            dict with mock recommendations
        """
        return {
            'topic': topic,
            'playlists': [
                {
                    'url': f'https://www.youtube.com/results?search_query={topic.replace(" ", "+")}+playlist',
                    'title': f'{topic} Complete Tutorial Playlist',
                    'channel': 'Educational Channel'
                },
                {
                    'url': f'https://www.youtube.com/results?search_query={topic.replace(" ", "+")}+course',
                    'title': f'{topic} Full Course',
                    'channel': 'Learning Platform'
                }
            ],
            'articles': [
                {
                    'url': f'https://www.google.com/search?q={topic.replace(" ", "+")}+tutorial',
                    'title': f'{topic} Tutorial and Guide',
                    'source': 'google'
                },
                {
                    'url': f'https://www.google.com/search?q={topic.replace(" ", "+")}+documentation',
                    'title': f'{topic} Official Documentation',
                    'source': 'google'
                }
            ],
            'questions': [
                {
                    'url': f'https://stackoverflow.com/search?q={topic.replace(" ", "+")}',
                    'title': f'Common questions about {topic}',
                    'votes': '100',
                    'source': 'stackoverflow'
                }
            ]
        }
    
    @staticmethod
    def get_recommendations_for_user(user):
        """
        Get all recommendations for a user's weak points
        
        Args:
            user: User instance
        
        Returns:
            dict with recommendations grouped by weak point
        """
        weak_points = WeakPoint.objects.filter(
            user=user,
            confidence_score__lt=0.7
        ).order_by('confidence_score')
        
        results = []
        
        for wp in weak_points:
            # Generate recommendations if not already done
            if not wp.recommendations_generated:
                RecommendationService.generate_recommendations(wp)
            
            # Get stored recommendations
            recommendations = CourseRecommendation.objects.filter(
                weak_point=wp
            ).order_by('-relevance_score')
            
            results.append({
                'weak_point': {
                    'id': wp.id,
                    'topic': wp.topic,
                    'subtopic': wp.subtopic,
                    'accuracy': wp.accuracy,
                    'confidence_score': wp.confidence_score
                },
                'recommendations': [
                    {
                        'id': rec.id,
                        'title': rec.title,
                        'url': rec.url,
                        'source': rec.source,
                        'description': rec.description,
                        'relevance_score': rec.relevance_score,
                        'viewed': rec.viewed
                    }
                    for rec in recommendations
                ]
            })
        
        return {
            'weak_points_count': len(results),
            'recommendations': results
        }
