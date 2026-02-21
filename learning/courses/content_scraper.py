"""
Content Scraper for Adaptive Learning
Integrates with Django to provide personalized recommendations
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests
import json


class ContentScraper:
    """Scraper for adaptive learning recommendations"""
    
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
    
    def init_driver(self):
        """Initialize undetected Chrome"""
        if not self.driver:
            options = uc.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            self.driver = uc.Chrome(options=options)
    
    def scrape_for_weak_topic(self, course_name, topic):
        """
        Main method: Scrape content for user's weak topic
        
        Args:
            course_name: e.g., "Python Programming"
            topic: e.g., "loops"
        
        Returns:
            dict with articles, playlists, questions
        """
        self.init_driver()
        
        search_query = f"{course_name} {topic}"
        
        return {
            'topic': topic,
            'articles': self._scrape_google(search_query),
            'playlists': self._scrape_youtube(search_query),
            'questions': self._get_stackoverflow(search_query)
        }
    
    def _scrape_google(self, query):
        """Scrape Google articles"""
        articles = []
        try:
            self.driver.get("https://www.google.com/")
            time.sleep(2)
            
            search_box = self.driver.find_element(By.NAME, "q")
            search_box.send_keys(f"{query} tutorial")
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)
            
            # Get results
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            seen_urls = set()
            
            for link in links[:30]:
                try:
                    href = link.get_attribute('href')
                    title = link.text
                    
                    if (href and href.startswith('http') and 
                        'google.com' not in href and 
                        href not in seen_urls and
                        title):
                        
                        articles.append({
                            'url': href,
                            'title': title[:100]  # Limit title length
                        })
                        seen_urls.add(href)
                        
                        if len(articles) >= 10:
                            break
                except:
                    continue
                    
        except Exception as e:
            print(f"Google scraping error: {e}")
        
        return articles
    
    def _scrape_youtube(self, query):
        """Scrape YouTube playlists"""
        playlists = []
        try:
            self.driver.get("https://www.youtube.com/")
            time.sleep(2)
            
            search_box = self.driver.find_element(By.NAME, "search_query")
            search_box.send_keys(f"{query} playlist")
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Get playlist links
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            seen_urls = set()
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    title = link.get_attribute('title')
                    
                    if href and 'list=' in href and href not in seen_urls:
                        clean_url = href.split('&')[0]
                        playlists.append({
                            'url': clean_url,
                            'title': title or query
                        })
                        seen_urls.add(href)
                        
                        if len(playlists) >= 10:
                            break
                except:
                    continue
                    
        except Exception as e:
            print(f"YouTube scraping error: {e}")
        
        return playlists
    
    def _get_stackoverflow(self, query):
        """Get Stack Overflow questions via API"""
        questions = []
        try:
            response = requests.get(
                'https://api.stackexchange.com/2.3/search',
                params={
                    'intitle': query,
                    'site': 'stackoverflow',
                    'order': 'desc',
                    'sort': 'votes',
                    'pagesize': 10
                },
                timeout=10
            )
            
            if response.status_code == 200:
                for item in response.json().get('items', []):
                    questions.append({
                        'title': item['title'],
                        'url': item['link'],
                        'score': item['score']
                    })
        except Exception as e:
            print(f"Stack Overflow API error: {e}")
        
        return questions
    
    def close(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass


def scrape_content_for_user(user, course):
    """
    Helper function to scrape content based on user's weak topics
    
    Args:
        user: Django User object
        course: Course object
    
    Returns:
        List of dicts with topic and scraped content
    """
    from .recommendations import get_weak_topics
    
    # Get weak topics
    weak_topics = get_weak_topics(user, course)
    
    if not weak_topics:
        return []
    
    # Scrape content for top 3 weak topics
    scraper = ContentScraper(headless=True)
    recommendations = []
    
    try:
        for topic in weak_topics[:3]:
            content = scraper.scrape_for_weak_topic(course.name, topic)
            recommendations.append(content)
    finally:
        scraper.close()
    
    return recommendations
