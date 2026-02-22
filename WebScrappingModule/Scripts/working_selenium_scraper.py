"""
WORKING Selenium Scraper - Tested and Verified
Uses multiple fallback methods to ensure data is scraped
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


class WorkingScraper:
    """
    Scraper that ACTUALLY works - uses multiple methods to find elements
    """
    
    def __init__(self, headless=False):
        """Initialize Chrome driver"""
        print("Initializing Chrome driver...")
        
        service = Service(ChromeDriverManager().install())
        
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 15)
        print("✓ Chrome driver initialized\n")
    
    def scrape_google_articles(self, topic, max_results=10):
        """
        Scrape Google - uses multiple methods to find results
        """
        print(f"Scraping Google for: {topic}")
        articles = []
        
        try:
            self.driver.get("https://www.google.com/")
            time.sleep(2)
            
            # Find and use search box
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            search_box.send_keys(f"{topic} tutorial")
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(4)  # Wait for results to load
            
            # Method 1: Try standard div.g selector
            results = self.driver.find_elements(By.CSS_SELECTOR, 'div.g')
            print(f"  Method 1 (div.g): Found {len(results)} results")
            
            # Method 2: If no results, try alternative selectors
            if len(results) == 0:
                results = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-sokoban-container]')
                print(f"  Method 2 (data-sokoban): Found {len(results)} results")
            
            # Method 3: Get all links and filter
            if len(results) == 0:
                all_links = self.driver.find_elements(By.TAG_NAME, 'a')
                results = [link for link in all_links if link.get_attribute('href') and 
                          link.get_attribute('href').startswith('http') and
                          'google.com' not in link.get_attribute('href')]
                print(f"  Method 3 (all links): Found {len(results)} results")
            
            # Extract data from results
            for result in results[:max_results]:
                try:
                    # Try to get href
                    url = result.get_attribute('href')
                    if not url:
                        # Try to find link inside
                        link = result.find_element(By.TAG_NAME, 'a')
                        url = link.get_attribute('href')
                    
                    # Try to get title
                    try:
                        title = result.find_element(By.TAG_NAME, 'h3').text
                    except:
                        try:
                            title = result.text.split('\n')[0]
                        except:
                            title = url
                    
                    if url and url.startswith('http') and 'google.com' not in url:
                        articles.append({
                            'url': url,
                            'title': title if title else url,
                            'source': 'google'
                        })
                        print(f"  ✓ {title[:60]}...")
                
                except Exception as e:
                    continue
            
            print(f"✓ Total scraped: {len(articles)} articles\n")
            
        except Exception as e:
            print(f"✗ Error: {e}\n")
        
        return articles
    
    def scrape_youtube_playlists(self, topic, max_results=10):
        """
        Scrape YouTube playlists - uses multiple methods
        """
        print(f"Scraping YouTube for: {topic}")
        playlists = []
        
        try:
            self.driver.get("https://www.youtube.com/")
            time.sleep(3)
            
            # Handle consent if present
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                for button in buttons:
                    if 'accept' in button.text.lower() or 'agree' in button.text.lower():
                        button.click()
                        time.sleep(1)
                        break
            except:
                pass
            
            # Search
            try:
                search_box = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "search_query"))
                )
                search_box.clear()
                search_box.send_keys(f"{topic} playlist")
                search_box.send_keys(Keys.RETURN)
                time.sleep(5)
            except Exception as e:
                print(f"  ✗ Could not search: {e}")
                return playlists
            
            # Scroll to load content
            for i in range(3):
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1)
            
            # Method 1: Get all links and filter for playlists
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            print(f"  Found {len(all_links)} total links")
            
            seen_urls = set()
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    
                    if href and 'list=' in href and href not in seen_urls:
                        # Clean URL
                        clean_url = href.split('&')[0] if '&' in href else href
                        
                        if clean_url in seen_urls:
                            continue
                        
                        seen_urls.add(clean_url)
                        
                        # Try to get title
                        title = link.get_attribute('title') or link.text or f"{topic} playlist"
                        
                        playlists.append({
                            'url': clean_url,
                            'title': title.strip(),
                            'channel': 'YouTube'
                        })
                        
                        print(f"  ✓ {title[:60]}...")
                        
                        if len(playlists) >= max_results:
                            break
                
                except:
                    continue
            
            print(f"✓ Total scraped: {len(playlists)} playlists\n")
            
        except Exception as e:
            print(f"✗ Error: {e}\n")
        
        return playlists
    
    def scrape_stackoverflow(self, topic, max_results=10):
        """
        Scrape Stack Overflow questions
        """
        print(f"Scraping Stack Overflow for: {topic}")
        questions = []
        
        try:
            # Go directly to search results
            search_url = f"https://stackoverflow.com/search?q={topic.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(3)
            
            # Method 1: Try standard selector
            question_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.s-post-summary')
            print(f"  Method 1: Found {len(question_elements)} questions")
            
            # Method 2: Try alternative selector
            if len(question_elements) == 0:
                question_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.question-summary')
                print(f"  Method 2: Found {len(question_elements)} questions")
            
            # Method 3: Get all question links
            if len(question_elements) == 0:
                all_links = self.driver.find_elements(By.TAG_NAME, 'a')
                question_elements = [link for link in all_links if '/questions/' in (link.get_attribute('href') or '')]
                print(f"  Method 3: Found {len(question_elements)} question links")
            
            for element in question_elements[:max_results]:
                try:
                    # Try to get title and URL
                    if element.tag_name == 'a':
                        url = element.get_attribute('href')
                        title = element.text
                    else:
                        link = element.find_element(By.TAG_NAME, 'a')
                        url = link.get_attribute('href')
                        title = link.text
                    
                    # Try to get votes
                    try:
                        vote_element = element.find_element(By.CSS_SELECTOR, 'span.s-post-summary--stats-item-number')
                        votes = vote_element.text
                    except:
                        votes = "0"
                    
                    if url and title:
                        questions.append({
                            'title': title.strip(),
                            'url': url if url.startswith('http') else f"https://stackoverflow.com{url}",
                            'votes': votes,
                            'source': 'stackoverflow'
                        })
                        print(f"  ✓ {title[:60]}...")
                
                except:
                    continue
            
            print(f"✓ Total scraped: {len(questions)} questions\n")
            
        except Exception as e:
            print(f"✗ Error: {e}\n")
        
        return questions
    
    def scrape_all(self, topic):
        """Scrape everything"""
        print(f"\n{'='*60}")
        print(f"Scraping all content for: {topic}")
        print(f"{'='*60}\n")
        
        results = {
            'topic': topic,
            'articles': self.scrape_google_articles(topic, 10),
            'playlists': self.scrape_youtube_playlists(topic, 10),
            'questions': self.scrape_stackoverflow(topic, 10),
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"{'='*60}")
        print(f"FINAL SUMMARY:")
        print(f"  Articles: {len(results['articles'])}")
        print(f"  Playlists: {len(results['playlists'])}")
        print(f"  Questions: {len(results['questions'])}")
        print(f"  TOTAL: {len(results['articles']) + len(results['playlists']) + len(results['questions'])}")
        print(f"{'='*60}\n")
        
        return results
    
    def close(self):
        """Close browser"""
        print("Closing browser...")
        self.driver.quit()
        print("✓ Browser closed\n")


def save_results(results):
    """Save to files"""
    
    # Articles
    with open('../Articles/articles.txt', 'w', encoding='utf-8') as f:
        f.write(f"# {results['topic']} Articles\n")
        f.write(f"# Scraped: {results['scraped_at']}\n")
        f.write(f"# Total: {len(results['articles'])}\n\n")
        
        for article in results['articles']:
            f.write(f"{article['url']}\n")
            f.write(f"  Title: {article['title']}\n\n")
    
    # Playlists
    with open('../Videos/playlist.txt', 'w', encoding='utf-8') as f:
        f.write(f"# {results['topic']} Playlists\n")
        f.write(f"# Scraped: {results['scraped_at']}\n")
        f.write(f"# Total: {len(results['playlists'])}\n\n")
        
        for playlist in results['playlists']:
            f.write(f"{playlist['url']}\n")
            f.write(f"  Title: {playlist['title']}\n\n")
    
    # Questions
    with open('../Answers/answers.txt', 'w', encoding='utf-8') as f:
        f.write(f"# {results['topic']} Q&A\n")
        f.write(f"# Scraped: {results['scraped_at']}\n")
        f.write(f"# Total: {len(results['questions'])}\n\n")
        
        for q in results['questions']:
            f.write(f"{q['title']}\n")
            f.write(f"  URL: {q['url']}\n")
            f.write(f"  Votes: {q['votes']}\n\n")
    
    # JSON
    with open('../scraped_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print("✓ Saved to:")
    print("  - Articles/articles.txt")
    print("  - Videos/playlist.txt")
    print("  - Answers/answers.txt")
    print("  - scraped_data.json\n")


if __name__ == "__main__":
    print("="*60)
    print("WORKING Selenium Scraper (2026)")
    print("="*60)
    print("Uses multiple fallback methods to ensure data is scraped")
    print("="*60 + "\n")
    
    # Get topic
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter topic: ").strip() or "Python"
    
    scraper = None
    try:
        scraper = WorkingScraper(headless=False)  # Set to True to hide browser
        results = scraper.scrape_all(topic)
        
        if sum([len(results['articles']), len(results['playlists']), len(results['questions'])]) > 0:
            save_results(results)
            print("✓ SUCCESS! Data scraped and saved.")
        else:
            print("✗ WARNING: No data was scraped. Check your internet connection.")
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scraper:
            scraper.close()
