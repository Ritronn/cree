"""
Scraper Service - Manages web scraping with caching and synchronous execution
Uses ScrapedContent model for caching and ScrapeJob for tracking scrapes.
Runs the actual UndetectedScraper and waits for results.
"""
import threading
import sys
from pathlib import Path
from datetime import timedelta
from django.utils import timezone
from .models import ScrapedContent, ScrapeJob


class ScraperService:
    """
    Manages web scraping with:
    1. DB-level caching (24-hour TTL)
    2. Synchronous scraper execution (waits for real data)
    3. Fallback only if scraper truly fails
    """
    
    CACHE_DURATION_HOURS = 24
    
    @classmethod
    def get_or_scrape(cls, topic):
        """
        Get cached scraper results or run the scraper synchronously.
        Always returns real scraped data — only falls back if scraper fails.
        
        Returns:
            dict with 'articles', 'playlists', 'questions', 'from_cache', 'scrape_status'
        """
        topic_clean = topic.strip().lower()
        
        # Check for fresh cached results first
        cached = cls.get_cached_results(topic_clean)
        
        if cached['total'] > 0 and not cached['expired']:
            return {
                **cached,
                'from_cache': True,
                'scrape_status': 'cached'
            }
        
        # No fresh cache — run the scraper synchronously and wait for results
        print(f"[ScraperService] No fresh cache for '{topic}', running scraper synchronously...")
        
        scrape_result = cls._run_scrape_sync(topic_clean)
        
        if scrape_result and scrape_result.get('total', 0) > 0:
            return {
                **scrape_result,
                'from_cache': False,
                'scrape_status': 'fresh'
            }
        
        # Scraper failed — check if we have stale cached data
        if cached['total'] > 0:
            print(f"[ScraperService] Scraper failed, returning stale cache for '{topic}'")
            return {
                **cached,
                'from_cache': True,
                'scrape_status': 'stale_cache'
            }
        
        # Last resort: fallback data
        print(f"[ScraperService] Scraper failed and no cache, using fallback for '{topic}'")
        from .recommendation_service import RecommendationService
        fallback = RecommendationService._get_fallback_recommendations(topic)
        
        return {
            'articles': fallback.get('articles', []),
            'playlists': fallback.get('playlists', []),
            'questions': fallback.get('questions', []),
            'total': len(fallback.get('articles', [])) + len(fallback.get('playlists', [])) + len(fallback.get('questions', [])),
            'expired': False,
            'scraped_at': None,
            'from_cache': False,
            'scrape_status': 'fallback'
        }
    
    @classmethod
    def get_or_scrape_async(cls, topic):
        """
        Non-blocking variant: returns cache immediately, triggers background scrape.
        Use this for endpoints where speed matters more than freshness.
        """
        topic_clean = topic.strip().lower()
        cached = cls.get_cached_results(topic_clean)
        
        if cached['total'] > 0 and not cached['expired']:
            return {**cached, 'from_cache': True, 'scrape_status': 'cached'}
        
        # Trigger background scrape
        cls._trigger_background_scrape(topic_clean)
        
        if cached['total'] > 0:
            return {**cached, 'from_cache': True, 'scrape_status': 'refreshing'}
        
        from .recommendation_service import RecommendationService
        fallback = RecommendationService._get_fallback_recommendations(topic)
        return {
            'articles': fallback.get('articles', []),
            'playlists': fallback.get('playlists', []),
            'questions': fallback.get('questions', []),
            'total': len(fallback.get('articles', [])) + len(fallback.get('playlists', [])) + len(fallback.get('questions', [])),
            'expired': False, 'scraped_at': None,
            'from_cache': False, 'scrape_status': 'scraping'
        }
    
    @classmethod
    def get_cached_results(cls, topic):
        """Get cached ScrapedContent for a topic."""
        topic_clean = topic.strip().lower()
        
        all_content = ScrapedContent.objects.filter(
            topic__iexact=topic_clean
        ).order_by('-scraped_at')
        
        if not all_content.exists():
            return {
                'articles': [], 'playlists': [], 'questions': [],
                'total': 0, 'expired': True, 'scraped_at': None
            }
        
        latest = all_content.first()
        is_expired = latest.is_expired
        
        articles, playlists, questions = [], [], []
        
        for item in all_content:
            entry = {'title': item.title, 'url': item.url, 'source': item.source}
            
            if item.source == 'google':
                articles.append(entry)
            elif item.source == 'youtube':
                entry['channel'] = item.channel or 'YouTube'
                playlists.append(entry)
            elif item.source == 'stackoverflow':
                entry['votes'] = item.votes or '0'
                questions.append(entry)
        
        return {
            'articles': articles[:10], 'playlists': playlists[:10],
            'questions': questions[:10],
            'total': len(articles) + len(playlists) + len(questions),
            'expired': is_expired,
            'scraped_at': latest.scraped_at.isoformat() if latest else None
        }
    
    @classmethod
    def _run_scrape_sync(cls, topic):
        """
        Run the scraper synchronously (blocking) and store results.
        Returns categorized results dict or None on failure.
        """
        # Create a tracking job
        job = ScrapeJob.objects.create(
            topic=topic, status='running', started_at=timezone.now()
        )
        
        try:
            results = cls._invoke_scraper(topic)
            
            if results:
                stored = cls._store_results(topic, results)
                
                job.status = 'completed'
                job.completed_at = timezone.now()
                job.result_count = stored
                job.save()
                
                print(f"[ScraperService] Scraped {stored} items for '{topic}'")
                
                # Return the fresh cached data
                return cls.get_cached_results(topic)
            else:
                job.status = 'failed'
                job.completed_at = timezone.now()
                job.error_message = 'Scraper returned no results'
                job.save()
                return None
                
        except Exception as e:
            print(f"[ScraperService] Scrape failed for '{topic}': {e}")
            job.status = 'failed'
            job.completed_at = timezone.now()
            job.error_message = str(e)[:500]
            job.save()
            return None
    
    @classmethod
    def _trigger_background_scrape(cls, topic):
        """Start a background scrape (non-blocking)."""
        topic_clean = topic.strip().lower()
        
        active = ScrapeJob.objects.filter(
            topic__iexact=topic_clean, status__in=['pending', 'running']
        )
        if active.exists():
            return
        
        job = ScrapeJob.objects.create(topic=topic_clean, status='pending')
        
        thread = threading.Thread(
            target=cls._background_scrape_worker,
            args=(job.id, topic_clean),
            daemon=True
        )
        thread.start()
    
    @classmethod
    def _background_scrape_worker(cls, job_id, topic):
        """Background thread worker for async scraping."""
        import django
        django.setup()
        from django.db import connection
        connection.close()
        
        try:
            job = ScrapeJob.objects.get(id=job_id)
            job.status = 'running'
            job.started_at = timezone.now()
            job.save()
            
            results = cls._invoke_scraper(topic)
            
            if results:
                stored = cls._store_results(topic, results)
                job.status = 'completed'
                job.completed_at = timezone.now()
                job.result_count = stored
                job.save()
            else:
                job.status = 'failed'
                job.completed_at = timezone.now()
                job.error_message = 'No results'
                job.save()
        except Exception as e:
            try:
                job = ScrapeJob.objects.get(id=job_id)
                job.status = 'failed'
                job.completed_at = timezone.now()
                job.error_message = str(e)[:500]
                job.save()
            except Exception:
                pass
    
    @classmethod
    def _invoke_scraper(cls, topic):
        """
        Import and run UndetectedScraper.
        Returns dict with 'articles', 'playlists', 'questions' or None.
        """
        project_root = Path(__file__).parent.parent.parent
        scraper_path = project_root / 'WebScrappingModule' / 'Scripts'
        
        if str(scraper_path) not in sys.path:
            sys.path.insert(0, str(scraper_path))
        
        try:
            from undetected_scraper import UndetectedScraper
            
            print(f"[ScraperService] Starting UndetectedScraper for: {topic}")
            scraper = UndetectedScraper(headless=False)  # Visible browser bypasses CAPTCHA
            
            try:
                results = scraper.scrape_all(topic)
                return results
            finally:
                try:
                    scraper.close()
                except Exception:
                    pass
                    
        except ImportError as e:
            print(f"[ScraperService] UndetectedScraper not available: {e}")
            
            try:
                from selenium_scraper_2026 import AdaptiveContentScraper
                scraper = AdaptiveContentScraper()
                results = scraper.scrape_all(topic)
                scraper.close()
                return results
            except ImportError:
                print(f"[ScraperService] No scraper available")
                return None
        except Exception as e:
            print(f"[ScraperService] Scraper error: {e}")
            return None
    
    @classmethod
    def _store_results(cls, topic, results):
        """Store scraped results in the ScrapedContent cache."""
        topic_clean = topic.strip().lower()
        expires_at = timezone.now() + timedelta(hours=cls.CACHE_DURATION_HOURS)
        
        # Delete old cached data
        ScrapedContent.objects.filter(topic__iexact=topic_clean).delete()
        
        stored_count = 0
        
        for article in results.get('articles', [])[:10]:
            try:
                ScrapedContent.objects.create(
                    topic=topic_clean, source='google',
                    title=article.get('title', '')[:500],
                    url=article.get('url', ''),
                    description=article.get('source', 'Web Article'),
                    expires_at=expires_at
                )
                stored_count += 1
            except Exception as e:
                print(f"[ScraperService] Store article error: {e}")
        
        for playlist in results.get('playlists', [])[:10]:
            try:
                ScrapedContent.objects.create(
                    topic=topic_clean, source='youtube',
                    title=playlist.get('title', '')[:500],
                    url=playlist.get('url', ''),
                    channel=playlist.get('channel', 'YouTube')[:200],
                    expires_at=expires_at
                )
                stored_count += 1
            except Exception as e:
                print(f"[ScraperService] Store playlist error: {e}")
        
        for question in results.get('questions', [])[:10]:
            try:
                ScrapedContent.objects.create(
                    topic=topic_clean, source='stackoverflow',
                    title=question.get('title', '')[:500],
                    url=question.get('url', ''),
                    votes=str(question.get('votes', '0'))[:20],
                    expires_at=expires_at
                )
                stored_count += 1
            except Exception as e:
                print(f"[ScraperService] Store question error: {e}")
        
        return stored_count
    
    @classmethod
    def get_scrape_status(cls, topic):
        """Get status of the most recent scrape job for a topic."""
        topic_clean = topic.strip().lower()
        
        job = ScrapeJob.objects.filter(
            topic__iexact=topic_clean
        ).order_by('-created_at').first()
        
        if not job:
            return {'status': 'none', 'message': 'No scrape job found'}
        
        return {
            'status': job.status,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'result_count': job.result_count,
            'error_message': job.error_message if job.status == 'failed' else None
        }
