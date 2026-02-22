# FINAL SOLUTION - Web Scraping for Adaptive Learning

## Current Status

### What Works ✅
- **YouTube Playlists**: 10 playlists scraped successfully
- **Selenium opens browser**: Works fine
- **Navigation**: Can access all sites

### What Doesn't Work ❌
- **Google Articles**: 0 results (anti-bot detection)
- **Stack Overflow**: 0 results (anti-bot detection)

## Root Cause

**Google and Stack Overflow detect Selenium and block scraping.**

They use:
- Bot detection scripts
- Cloudflare protection
- CAPTCHA challenges
- Fingerprinting

---

## SOLUTION: Hybrid Approach

For your adaptive learning system, use a **combination**:

### 1. YouTube → Use Selenium ✅
**Why:** Works perfectly, gets actual playlist links
```python
# YouTube scraping works!
playlists = scraper.scrape_youtube_playlists("React hooks")
# Returns: 10 actual playlist URLs
```

### 2. Google Articles → Use API ✅
**Why:** Google Custom Search API is free and reliable
```python
import requests

def get_google_articles(topic, api_key, cx):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cx,
        'q': f"{topic} tutorial",
        'num': 10
    }
    response = requests.get(url, params=params)
    return response.json()['items']

# Get API key: https://developers.google.com/custom-search
# Free tier: 100 searches/day
```

### 3. Stack Overflow → Use API ✅
**Why:** Stack Exchange API is free and doesn't need authentication
```python
import requests

def get_stackoverflow_questions(topic):
    url = "https://api.stackexchange.com/2.3/search"
    params = {
        'order': 'desc',
        'sort': 'votes',
        'intitle': topic,
        'site': 'stackoverflow'
    }
    response = requests.get(url, params=params)
    return response.json()['items']

# No API key needed!
# Free tier: 10,000 requests/day
```

---

## RECOMMENDED IMPLEMENTATION

### For Your Adaptive Learning System:

```python
# learning/courses/content_scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time


class AdaptiveLearningContentScraper:
    """
    Hybrid scraper for adaptive learning
    - YouTube: Selenium (works great)
    - Google: API (reliable)
    - Stack Overflow: API (reliable)
    """
    
    def __init__(self, google_api_key=None, google_cx=None):
        self.google_api_key = google_api_key
        self.google_cx = google_cx
        self.driver = None
    
    def init_selenium(self):
        """Initialize Selenium only when needed (for YouTube)"""
        if not self.driver:
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Run in background
            self.driver = webdriver.Chrome(service=service, options=options)
    
    def get_youtube_playlists(self, topic, max_results=10):
        """
        Get YouTube playlists using Selenium (WORKS!)
        """
        self.init_selenium()
        playlists = []
        
        try:
            self.driver.get("https://www.youtube.com/")
            time.sleep(2)
            
            # Search
            search_box = self.driver.find_element(By.NAME, "search_query")
            search_box.send_keys(f"{topic} playlist")
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Get playlist links
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            for link in all_links:
                href = link.get_attribute('href')
                if href and 'list=' in href:
                    playlists.append({
                        'url': href.split('&')[0],
                        'title': link.get_attribute('title') or topic,
                        'source': 'youtube'
                    })
                    if len(playlists) >= max_results:
                        break
        
        except Exception as e:
            print(f"YouTube error: {e}")
        
        return playlists
    
    def get_google_articles(self, topic, max_results=10):
        """
        Get articles using Google Custom Search API (RELIABLE!)
        """
        articles = []
        
        if not self.google_api_key or not self.google_cx:
            # Fallback: Return curated content
            return self._get_curated_articles(topic)
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cx,
                'q': f"{topic} tutorial",
                'num': max_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            for item in data.get('items', []):
                articles.append({
                    'url': item['link'],
                    'title': item['title'],
                    'source': 'google'
                })
        
        except Exception as e:
            print(f"Google API error: {e}")
            # Fallback to curated content
            articles = self._get_curated_articles(topic)
        
        return articles
    
    def get_stackoverflow_questions(self, topic, max_results=10):
        """
        Get questions using Stack Exchange API (RELIABLE!)
        """
        questions = []
        
        try:
            url = "https://api.stackexchange.com/2.3/search"
            params = {
                'order': 'desc',
                'sort': 'votes',
                'intitle': topic,
                'site': 'stackoverflow',
                'pagesize': max_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            for item in data.get('items', []):
                questions.append({
                    'title': item['title'],
                    'url': item['link'],
                    'score': item['score'],
                    'source': 'stackoverflow'
                })
        
        except Exception as e:
            print(f"Stack Overflow API error: {e}")
        
        return questions
    
    def _get_curated_articles(self, topic):
        """Fallback: Curated content for common topics"""
        curated = {
            'python': [
                {'url': 'https://docs.python.org/3/tutorial/', 'title': 'Official Python Tutorial'},
                {'url': 'https://realpython.com/', 'title': 'Real Python'},
            ],
            'javascript': [
                {'url': 'https://javascript.info/', 'title': 'JavaScript.info'},
                {'url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript', 'title': 'MDN JavaScript'},
            ],
            'react': [
                {'url': 'https://react.dev/', 'title': 'Official React Docs'},
                {'url': 'https://react.dev/learn', 'title': 'React Tutorial'},
            ]
        }
        
        for key in curated:
            if key in topic.lower():
                return curated[key]
        
        return []
    
    def scrape_for_weak_topic(self, topic):
        """
        Main method: Scrape content for a weak topic
        """
        return {
            'topic': topic,
            'playlists': self.get_youtube_playlists(topic, 5),
            'articles': self.get_google_articles(topic, 5),
            'questions': self.get_stackoverflow_questions(topic, 5)
        }
    
    def close(self):
        """Close Selenium driver"""
        if self.driver:
            self.driver.quit()


# Usage in Django
def get_content_for_weak_topics(user, course):
    """
    Get personalized content based on user's weak areas
    """
    from courses.recommendations import get_weak_topics
    
    # Get weak topics
    weak_topics = get_weak_topics(user, course)
    
    # Initialize scraper
    scraper = AdaptiveLearningContentScraper(
        google_api_key='YOUR_API_KEY',  # Optional
        google_cx='YOUR_CX'  # Optional
    )
    
    # Scrape content for each weak topic
    recommendations = []
    for topic in weak_topics[:3]:  # Top 3 weak topics
        content = scraper.scrape_for_weak_topic(f"{course.subject} {topic}")
        recommendations.append(content)
    
    scraper.close()
    
    return recommendations
```

---

## API Setup (Optional but Recommended)

### Google Custom Search API
1. Go to: https://developers.google.com/custom-search/v1/overview
2. Create project
3. Enable Custom Search API
4. Get API key
5. Create Custom Search Engine: https://cse.google.com/cse/
6. Get CX (Search Engine ID)

**Free Tier:** 100 searches/day

### Stack Exchange API
- No setup needed!
- No API key required
- Free: 10,000 requests/day
- Just use: https://api.stackexchange.com/2.3/search

---

## What You Get

### With This Hybrid Approach:

```python
# User weak in "React hooks"
content = scraper.scrape_for_weak_topic("React hooks")

# Returns:
{
  'topic': 'React hooks',
  'playlists': [
    {'url': 'https://youtube.com/playlist?list=...', 'title': 'React Hooks Course'},
    {'url': 'https://youtube.com/playlist?list=...', 'title': 'useState Tutorial'},
    # ... 5 playlists
  ],
  'articles': [
    {'url': 'https://react.dev/hooks', 'title': 'React Hooks Documentation'},
    {'url': 'https://blog.com/react-hooks', 'title': 'React Hooks Guide'},
    # ... 5 articles
  ],
  'questions': [
    {'title': 'How to use useState?', 'url': '...', 'score': 1234},
    {'title': 'useEffect best practices', 'url': '...', 'score': 890},
    # ... 5 questions
  ]
}
```

---

## Summary

### Current Selenium Scraper:
- ✅ YouTube: Works (10 playlists)
- ❌ Google: Blocked by anti-bot
- ❌ Stack Overflow: Blocked by anti-bot

### Recommended Solution:
- ✅ YouTube: Use Selenium (works great!)
- ✅ Google: Use API (reliable, 100/day free)
- ✅ Stack Overflow: Use API (reliable, 10k/day free)

### For Your Adaptive Learning:
```python
# Perfect workflow:
1. User takes quiz → scores low on "loops"
2. System identifies weak topic: "Python loops"
3. Scraper gets:
   - 5 YouTube playlists (Selenium)
   - 5 articles (Google API or curated)
   - 5 Stack Overflow questions (API)
4. Show personalized recommendations to user
```

---

## Quick Start

```bash
# Install
pip install selenium webdriver-manager requests

# Test YouTube scraping (works!)
python working_selenium_scraper.py "React hooks"
# Result: 10 YouTube playlists ✓

# For Google & Stack Overflow:
# Use APIs (more reliable than scraping)
```

---

## Final Recommendation

**For production adaptive learning system:**

1. **YouTube playlists** → Use Selenium (working!)
2. **Articles** → Use Google API or curated content
3. **Q&A** → Use Stack Exchange API

This gives you:
- ✅ Reliable data collection
- ✅ No anti-bot issues
- ✅ Fast performance
- ✅ Free (within limits)
- ✅ Perfect for adaptive learning

**The hybrid approach is the best solution for your use case!**
