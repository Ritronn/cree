"""
Adaptive Suggestions API Views
Provides personalized content suggestions based on weak points and study topics
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import WeakPoint, CourseRecommendation, Topic
from .recommendation_service import RecommendationService
from .coursera_service import CourseraService
from .scraper_service import ScraperService


class AdaptiveSuggestionViewSet(viewsets.ViewSet):
    """
    Adaptive content suggestions based on weak points
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def weak_point_suggestions(self, request):
        """
        Get adaptive suggestions for user's weak points
        If no weak points exist, use study session workspace names
        Includes YouTube playlists, articles, and Q&A
        """
        # Get user's weak points
        weak_points = WeakPoint.objects.filter(
            user=request.user,
            confidence_score__lt=0.7
        ).order_by('confidence_score')[:10]
        
        suggestions = []
        
        # If weak points exist, use them
        if weak_points.exists():
            for wp in weak_points:
                # Check if recommendations already exist
                existing_recommendations = CourseRecommendation.objects.filter(
                    weak_point=wp
                ).order_by('-relevance_score')[:10]
                
                if existing_recommendations.exists():
                    # Use existing recommendations
                    suggestions.append({
                        'weak_point': {
                            'id': wp.id,
                            'topic': wp.topic,
                            'subtopic': wp.subtopic,
                            'accuracy': wp.accuracy,
                            'confidence_score': wp.confidence_score,
                            'incorrect_count': wp.incorrect_count,
                            'total_attempts': wp.total_attempts
                        },
                        'suggestions': [
                            {
                                'id': rec.id,
                                'title': rec.title,
                                'url': rec.url,
                                'source': rec.source,
                                'description': rec.description,
                                'relevance_score': rec.relevance_score,
                                'viewed': rec.viewed,
                                'created_at': rec.created_at
                            }
                            for rec in existing_recommendations
                        ]
                    })
                else:
                    # Generate new recommendations using REAL scraper
                    scraper_data = ScraperService.get_or_scrape(wp.topic)
                    
                    # Store scraped results in CourseRecommendation DB for next time
                    for playlist in scraper_data.get('playlists', [])[:5]:
                        CourseRecommendation.objects.get_or_create(
                            weak_point=wp,
                            url=playlist['url'],
                            defaults={
                                'user': wp.user,
                                'title': playlist['title'],
                                'source': 'youtube',
                                'description': playlist.get('channel', 'YouTube'),
                                'relevance_score': 0.9
                            }
                        )
                    
                    for article in scraper_data.get('articles', [])[:5]:
                        CourseRecommendation.objects.get_or_create(
                            weak_point=wp,
                            url=article['url'],
                            defaults={
                                'user': wp.user,
                                'title': article['title'],
                                'source': 'article',
                                'description': article.get('source', 'Web Article'),
                                'relevance_score': 0.8
                            }
                        )
                    
                    for question in scraper_data.get('questions', [])[:3]:
                        CourseRecommendation.objects.get_or_create(
                            weak_point=wp,
                            url=question['url'],
                            defaults={
                                'user': wp.user,
                                'title': question['title'],
                                'source': 'stackoverflow',
                                'description': f"{question.get('votes', '0')} votes",
                                'relevance_score': 0.7
                            }
                        )
                    
                    wp.recommendations_generated = True
                    wp.save()
                    
                    # Get the newly created recommendations
                    new_recommendations = CourseRecommendation.objects.filter(
                        weak_point=wp
                    ).order_by('-relevance_score')[:10]
                    
                    suggestions.append({
                        'weak_point': {
                            'id': wp.id,
                            'topic': wp.topic,
                            'subtopic': wp.subtopic,
                            'accuracy': wp.accuracy,
                            'confidence_score': wp.confidence_score,
                            'incorrect_count': wp.incorrect_count,
                            'total_attempts': wp.total_attempts
                        },
                        'suggestions': [
                            {
                                'id': rec.id,
                                'title': rec.title,
                                'url': rec.url,
                                'source': rec.source,
                                'description': rec.description,
                                'relevance_score': rec.relevance_score,
                                'viewed': rec.viewed,
                                'created_at': rec.created_at
                            }
                            for rec in new_recommendations
                        ]
                    })
        else:
            # No weak points - use study session workspace names
            from .models import StudySession
            
            # Get recent study sessions with workspace names
            recent_sessions = StudySession.objects.filter(
                user=request.user,
                is_completed=True
            ).exclude(
                workspace_name__isnull=True
            ).exclude(
                workspace_name__exact=''
            ).order_by('-ended_at')[:5]
            
            # Extract unique workspace names (these are the topics!)
            topics_seen = set()
            
            for session in recent_sessions:
                topic_name = session.workspace_name.strip()
                
                # Skip generic names and duplicates
                if topic_name and topic_name not in topics_seen and len(topic_name) > 2:
                    topics_seen.add(topic_name)
                    
                    # Use ScraperService for cached/background scraping
                    print(f"Getting suggestions for workspace topic: {topic_name}")
                    scraper_data = ScraperService.get_or_scrape(topic_name)
                    
                    # Format as suggestion
                    suggestions.append({
                        'weak_point': {
                            'id': None,
                            'topic': topic_name,
                            'subtopic': 'Study Session Topic',
                            'accuracy': 100.0,
                            'confidence_score': 1.0,
                            'incorrect_count': 0,
                            'total_attempts': 0
                        },
                        'suggestions': [
                            {
                                'id': None,
                                'title': item['title'],
                                'url': item['url'],
                                'source': 'youtube',
                                'description': item.get('channel', 'YouTube'),
                                'relevance_score': 0.8,
                                'viewed': False,
                                'created_at': None
                            }
                            for item in scraper_data.get('playlists', [])[:5]
                        ] + [
                            {
                                'id': None,
                                'title': item['title'],
                                'url': item['url'],
                                'source': 'article',
                                'description': item.get('source', 'Web Article'),
                                'relevance_score': 0.7,
                                'viewed': False,
                                'created_at': None
                            }
                            for item in scraper_data.get('articles', [])[:5]
                        ] + [
                            {
                                'id': None,
                                'title': item['title'],
                                'url': item['url'],
                                'source': 'stackoverflow',
                                'description': f"{item.get('votes', '0')} votes",
                                'relevance_score': 0.6,
                                'viewed': False,
                                'created_at': None
                            }
                            for item in scraper_data.get('questions', [])[:3]
                        ],
                        'scrape_status': scraper_data.get('scrape_status', 'unknown'),
                        'scraped_at': scraper_data.get('scraped_at', None)
                    })
            
            # If still no suggestions, use recent topics from Topic model
            if not suggestions:
                recent_topics = Topic.objects.filter(
                    user=request.user
                ).order_by('-updated_at')[:3]
                
                for topic in recent_topics:
                    scraper_data = ScraperService.get_or_scrape(topic.name)
                    
                    suggestions.append({
                        'weak_point': {
                            'id': None,
                            'topic': topic.name,
                            'subtopic': 'Recent Study Topic',
                            'accuracy': topic.mastery_level * 100,
                            'confidence_score': topic.mastery_level,
                            'incorrect_count': 0,
                            'total_attempts': 0
                        },
                        'suggestions': [
                            {
                                'id': None,
                                'title': item['title'],
                                'url': item['url'],
                                'source': 'youtube',
                                'description': item.get('channel', 'YouTube'),
                                'relevance_score': 0.8,
                                'viewed': False,
                                'created_at': None
                            }
                            for item in scraper_data.get('playlists', [])[:5]
                        ] + [
                            {
                                'id': None,
                                'title': item['title'],
                                'url': item['url'],
                                'source': 'article',
                                'description': item.get('source', 'Web Article'),
                                'relevance_score': 0.7,
                                'viewed': False,
                                'created_at': None
                            }
                            for item in scraper_data.get('articles', [])[:5]
                        ] + [
                            {
                                'id': None,
                                'title': item['title'],
                                'url': item['url'],
                                'source': 'stackoverflow',
                                'description': f"{item.get('votes', '0')} votes",
                                'relevance_score': 0.6,
                                'viewed': False,
                                'created_at': None
                            }
                            for item in scraper_data.get('questions', [])[:3]
                        ],
                        'scrape_status': scraper_data.get('scrape_status', 'unknown'),
                        'scraped_at': scraper_data.get('scraped_at', None)
                    })
        
        return Response({
            'success': True,
            'weak_points_count': len(suggestions),
            'suggestions': suggestions,
            'fallback_used': not weak_points.exists(),
            'using_curated_data': True  # Let frontend know we're using fast curated data
        })
    
    @action(detail=False, methods=['get'])
    def recent_topic_suggestions(self, request):
        """
        Get course suggestions based on recent study topics
        """
        # Get user's recent topics
        recent_topics = Topic.objects.filter(
            user=request.user
        ).order_by('-updated_at')[:5]
        
        suggestions = []
        
        for topic in recent_topics:
            # Use ScraperService for cached/background scraping
            scraper_results = ScraperService.get_or_scrape(topic.name)
            
            suggestions.append({
                'topic': {
                    'id': topic.id,
                    'name': topic.name,
                    'description': topic.description,
                    'mastery_level': topic.mastery_level,
                    'current_difficulty': topic.current_difficulty
                },
                'playlists': scraper_results.get('playlists', [])[:5],
                'articles': scraper_results.get('articles', [])[:5],
                'questions': scraper_results.get('questions', [])[:3]
            })
        
        return Response({
            'success': True,
            'topics_count': len(suggestions),
            'suggestions': suggestions
        })
    
    @action(detail=False, methods=['get'])
    def coursera_certificates(self, request):
        """
        Get Coursera certificate recommendations
        Based on both recent topics and weak points
        """
        # Get recommendations for recent topics
        topic_certificates = CourseraService.get_recommendations_for_user(request.user)
        
        # Get recommendations for weak points
        weak_point_certificates = CourseraService.get_recommendations_for_weak_points(request.user)
        
        # Combine and deduplicate
        all_certificates = {}
        
        for cert in topic_certificates:
            url = cert['url']
            if url not in all_certificates:
                all_certificates[url] = {
                    **cert,
                    'recommendation_reason': 'Based on your recent study topics'
                }
        
        for cert in weak_point_certificates:
            url = cert['url']
            if url not in all_certificates:
                all_certificates[url] = {
                    **cert,
                    'recommendation_reason': 'Recommended to strengthen weak areas'
                }
        
        # Convert to list and sort by relevance
        certificate_list = list(all_certificates.values())
        certificate_list.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return Response({
            'success': True,
            'certificates_count': len(certificate_list),
            'certificates': certificate_list[:15]  # Top 15
        })
    
    @action(detail=False, methods=['post'])
    def mark_suggestion_viewed(self, request):
        """
        Mark a suggestion as viewed
        """
        suggestion_id = request.data.get('suggestion_id')
        
        if not suggestion_id:
            return Response(
                {'error': 'suggestion_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            recommendation = CourseRecommendation.objects.get(
                id=suggestion_id,
                user=request.user
            )
            recommendation.viewed = True
            recommendation.save()
            
            return Response({
                'success': True,
                'message': 'Suggestion marked as viewed'
            })
        except CourseRecommendation.DoesNotExist:
            return Response(
                {'error': 'Suggestion not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def refresh_suggestions(self, request):
        """
        Force refresh suggestions for a weak point
        """
        weak_point_id = request.data.get('weak_point_id')
        
        if not weak_point_id:
            return Response(
                {'error': 'weak_point_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            weak_point = WeakPoint.objects.get(
                id=weak_point_id,
                user=request.user
            )
            
            # Delete old recommendations
            CourseRecommendation.objects.filter(weak_point=weak_point).delete()
            
            # Generate new ones
            result = RecommendationService.generate_recommendations(weak_point)
            
            return Response({
                'success': True,
                'message': 'Suggestions refreshed',
                **result
            })
        except WeakPoint.DoesNotExist:
            return Response(
                {'error': 'Weak point not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def scraper_status(self, request):
        """
        Get scraper status for user's recent topics
        """
        from .models import StudySession
        
        # Get recent workspace names
        recent_sessions = StudySession.objects.filter(
            user=request.user,
            is_completed=True
        ).exclude(
            workspace_name__isnull=True
        ).exclude(
            workspace_name__exact=''
        ).order_by('-ended_at')[:5]
        
        statuses = []
        seen = set()
        
        for session in recent_sessions:
            topic = session.workspace_name.strip()
            if topic and topic not in seen:
                seen.add(topic)
                status_info = ScraperService.get_scrape_status(topic)
                statuses.append({
                    'topic': topic,
                    **status_info
                })
        
        return Response({
            'success': True,
            'scraper_statuses': statuses
        })
