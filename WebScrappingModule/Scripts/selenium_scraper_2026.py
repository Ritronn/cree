"""
Updated Selenium Scraper for 2026
For dynamic, real-time content scraping based on user needs
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import sys


class AdaptiveContentScraper:
    """
    Scraper for adaptive learning system
    Dynamically scrapes content based on user's weak areas
    """
    
    def __init__(self):
        """Initialize Chrome driver with automatic driver management"""
        print("Initializing Chrome driver...")
        
        # Use webdriver-manager for automatic driver management
        service = Service(ChromeDriverManager().install())
        
        # Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        print("✓ Chrome driver initialized")
    
    def scrape_google_articles(self, topic, max_results=10):
        """
        Scrape article links from Google search
        
        Args:
            topic: Topic to search for
            max_results: Maximum number of results to return
        
        Returns:
            List of article dictionaries
        """
        print(f"\nScraping Google articles for: {topic}")
        articles = []
        
        try:
            # Go to Google
            self.driver.get("https://www.google.com/")
            time.sleep(2)
            
            # Find search box and search
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.send_keys(f"{topic} tutorial")
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(3)
            
            # Get search results (updated selectors for 2026)
            results = self.driver.find_elements(By.CSS_SELECTOR, 'div.g')
            
            print(f"Found {len(results)} search results")
            
            for result in results[:max_results]:
                try:
                    # Get link
                    link_element = result.find_element(By.TAG_NAME, 'a')
                    url = link_element.get_attribute('href')
                    
                    # Get title
                    try:
                        title_element = result.find_element(By.TAG_NAME, 'h3')
                        title = title_element.text
                    except:
                        title = url
                    
                    if url and url.startswith('http'):
                        articles.append({
                            'url': url,
                            'title': title,
                            'source': 'google'
                        })
                        print(f"  ✓ {title[:60]}...")
                
                except Exception as e:
                    continue
            
            print(f"✓ Scraped {len(articles)} articles")
            
        except Exception as e:
            print(f"✗ Error scraping Google: {e}")
        
        return articles
    
    def scrape_youtube_playlists(self, topic, max_results=10):
        """
        Scrape actual YouTube playlist links (not just search URL!)
        
        Args:
            topic: Topic to search for
            max_results: Maximum number of playlists to return
        
        Returns:
            List of playlist dictionaries
        """
        print(f"\nScraping YouTube playlists for: {topic}")
        playlists = []
        
        try:
            # Go to YouTube
            self.driver.get("https://www.youtube.com/")
            time.sleep(3)
            
            # Handle cookie consent if present
            try:
                accept_button = self.driver.find_element(
                    By.XPATH, 
                    "//button[@aria-label='Accept all']"
                )
                accept_button.click()
                time.sleep(1)
            except:
                pass
            
            # Find search box
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            search_box.clear()
            search_box.send_keys(f"{topic} playlist")
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(5)
            
            # Click on Playlists filter
            try:
                # Try multiple selectors for the Playlists filter
                playlist_filter = None
                
                # Method 1: By text
                try:
                    playlist_filter = self.driver.find_element(
                        By.XPATH, 
                        "//yt-formatted-string[contains(text(), 'Playlists')]"
                    )
                except:
                    pass
                
                # Method 2: By chip-bar
                if not playlist_filter:
                    try:
                        filters = self.driver.find_elements(By.CSS_SELECTOR, 'yt-chip-cloud-chip-renderer')
                        for f in filters:
                            if 'playlist' in f.text.lower():
                                playlist_filter = f
                                break
                    except:
                        pass
                
                if playlist_filter:
                    playlist_filter.click()
                    time.sleep(3)
                    print("  ✓ Filtered by playlists")
                else:
                    print("  ⚠ Could not find playlist filter, showing all results")
            
            except Exception as e:
                print(f"  ⚠ Could not filter by playlists: {e}")
            
            # Scroll to load more results
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1)
            
            # Get playlist links
            # Try multiple selectors
            playlist_elements = []
            
            # Method 1: ytd-playlist-renderer
            try:
                playlist_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    'ytd-playlist-renderer a#thumbnail'
                )
            except:
                pass
            
            # Method 2: Generic playlist links
            if not playlist_elements:
                try:
                    all_links = self.driver.find_elements(By.TAG_NAME, 'a')
                    playlist_elements = [
                        link for link in all_links 
                        if 'list=' in link.get_attribute('href') or ''
                    ]
                except:
                    pass
            
            print(f"Found {len(playlist_elements)} playlist elements")
            
            seen_urls = set()
            
            for element in playlist_elements[:max_results * 2]:  # Get extra in case of duplicates
                try:
                    url = element.get_attribute('href')
                    
                    if url and 'list=' in url and url not in seen_urls:
                        seen_urls.add(url)
                        
                        # Try to get title
                        try:
                            # Try to find title in parent elements
                            parent = element.find_element(By.XPATH, './ancestor::ytd-playlist-renderer')
                            title_element = parent.find_element(By.ID, 'video-title')
                            title = title_element.text
                        except:
                            try:
                                title = element.get_attribute('title')
                            except:
                                title = f"Playlist for {topic}"
                        
                        # Try to get channel name
                        try:
                            channel_element = parent.find_element(By.CSS_SELECTOR, 'yt-formatted-string.ytd-channel-name')
                            channel = channel_element.text
                        except:
                            channel = "Unknown"
                        
                        playlists.append({
                            'url': url.split('&')[0],  # Clean URL
                            'title': title,
                            'channel': channel
                        })
                        
                        print(f"  ✓ {title[:60]}... by {channel}")
                        
                        if len(playlists) >= max_results:
                            break
                
                except Exception as e:
                    continue
            
            print(f"✓ Scraped {len(playlists)} playlists")
            
        except Exception as e:
            print(f"✗ Error scraping YouTube: {e}")
            import traceback
            traceback.print_exc()
        
        return playlists
    
    def scrape_stackoverflow_questions(self, topic, max_results=10):
        """
        Scrape Stack Overflow questions
        
        Args:
            topic: Topic to search for
            max_results: Maximum number of questions to return
        
        Returns:
            List of question dictionaries
        """
        print(f"\nScraping Stack Overflow for: {topic}")
        questions = []
        
        try:
            # Go to Stack Overflow
            search_url = f"https://stackoverflow.com/search?q={topic.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(3)
            
            # Get question elements
            question_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                'div.s-post-summary'
            )
            
            print(f"Found {len(question_elements)} questions")
            
            for element in question_elements[:max_results]:
                try:
                    # Get title and link
                    title_element = element.find_element(By.CSS_SELECTOR, 'h3 a')
                    title = title_element.text
                    url = title_element.get_attribute('href')
                    
                    # Get vote count
                    try:
                        vote_element = element.find_element(By.CSS_SELECTOR, 'span.s-post-summary--stats-item-number')
                        votes = vote_element.text
                    except:
                        votes = "0"
                    
                    questions.append({
                        'title': title,
                        'url': url if url.startswith('http') else f"https://stackoverflow.com{url}",
                        'votes': votes,
                        'source': 'stackoverflow'
                    })
                    
                    print(f"  ✓ {title[:60]}... ({votes} votes)")
                
                except Exception as e:
                    continue
            
            print(f"✓ Scraped {len(questions)} questions")
            
        except Exception as e:
            print(f"✗ Error scraping Stack Overflow: {e}")
        
        return questions
    
    def scrape_all(self, topic):
        """
        Scrape all content types for a topic
        
        Args:
            topic: Topic to scrape
        
        Returns:
            Dictionary with all scraped content
        """
        print(f"\n{'='*60}")
        print(f"Scraping all content for: {topic}")
        print(f"{'='*60}")
        
        results = {
            'topic': topic,
            'articles': self.scrape_google_articles(topic, max_results=10),
            'playlists': self.scrape_youtube_playlists(topic, max_results=10),
            'questions': self.scrape_stackoverflow_questions(topic, max_results=10),
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Articles: {len(results['articles'])}")
        print(f"  Playlists: {len(results['playlists'])}")
        print(f"  Questions: {len(results['questions'])}")
        print(f"{'='*60}")
        
        return results
    
    def close(self):
        """Close the browser"""
        print("\nClosing browser...")
        self.driver.quit()
        print("✓ Browser closed")


def save_results(results):
    """Save results to files"""
    
    # Save articles
    with open('../Articles/articles.txt', 'w', encoding='utf-8') as f:
        f.write(f"# {results['topic']} Articles\n")
        f.write(f"# Scraped: {results['scraped_at']}\n\n")
        
        for article in results['articles']:
            f.write(f"{article['url']}\n")
            f.write(f"  Title: {article['title']}\n")
            f.write(f"  Source: {article['source']}\n\n")
    
    # Save playlists
    with open('../Videos/playlist.txt', 'w', encoding='utf-8') as f:
        f.write(f"# {results['topic']} YouTube Playlists\n")
        f.write(f"# Scraped: {results['scraped_at']}\n\n")
        
        for playlist in results['playlists']:
            f.write(f"{playlist['url']}\n")
            f.write(f"  Title: {playlist['title']}\n")
            f.write(f"  Channel: {playlist['channel']}\n\n")
    
    # Save questions
    with open('../Answers/answers.txt', 'w', encoding='utf-8') as f:
        f.write(f"# {results['topic']} Q&A\n")
        f.write(f"# Scraped: {results['scraped_at']}\n\n")
        
        for question in results['questions']:
            f.write(f"{question['title']}\n")
            f.write(f"  URL: {question['url']}\n")
            f.write(f"  Votes: {question['votes']}\n")
            f.write(f"  Source: {question['source']}\n\n")
    
    # Save JSON
    with open('../scraped_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print("\n✓ Results saved to:")
    print("  - Articles/articles.txt")
    print("  - Videos/playlist.txt")
    print("  - Answers/answers.txt")
    print("  - scraped_data.json")


if __name__ == "__main__":
    print("="*60)
    print("Selenium-Based Adaptive Content Scraper (2026)")
    print("="*60)
    print("\nFeatures:")
    print("  ✓ Real-time scraping (not curated content)")
    print("  ✓ Actual playlist links (not search URLs)")
    print("  ✓ Dynamic content based on user needs")
    print("  ✓ Perfect for adaptive learning systems")
    print("\n" + "="*60 + "\n")
    
    # Get topic
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter topic to scrape: ").strip()
        if not topic:
            topic = "Python"
    
    scraper = None
    try:
        scraper = AdaptiveContentScraper()
        results = scraper.scrape_all(topic)
        save_results(results)
        print("\n✓ Scraping completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scraper:
            scraper.close()
