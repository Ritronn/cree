"""
Undetected Scraper - Bypasses all anti-bot detection
Uses undetected-chromedriver to scrape Google, Stack Overflow, etc.
100% FREE and works perfectly!
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import sys


class UndetectedScraper:
    """
    Scraper that bypasses ALL anti-bot detection
    Works on Google, Stack Overflow, YouTube, everything!
    """
    
    def __init__(self, headless=False):
        """Initialize undetected Chrome driver"""
        print("Initializing undetected Chrome driver...")
        
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        
        # undetected-chromedriver automatically bypasses detection!
        self.driver = uc.Chrome(options=options, version_main=None)
        self.wait = WebDriverWait(self.driver, 15)
        print("✓ Undetected driver initialized (anti-bot bypassed!)\n")
    
    def scrape_google(self, topic, max_results=10):
        """
        Scrape Google - WORKS because undetected!
        """
        print(f"Scraping Google for: {topic}")
        articles = []
        
        try:
            # Go to Google
            self.driver.get("https://www.google.com/")
            time.sleep(3)
            
            # Search
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            search_box.send_keys(f"{topic} tutorial")
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(4)
            
            # Get all links
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    
                    # Filter valid URLs
                    if (href and 
                        href.startswith('http') and 
                        'google.com' not in href and
                        'youtube.com' not in href):
                        
                        # Get title
                        try:
                            # Try to find h3 in parent
                            parent = link.find_element(By.XPATH, './ancestor::div[@class="g"]')
                            title = parent.find_element(By.TAG_NAME, 'h3').text
                        except:
                            title = link.text or href
                        
                        if title and len(title) > 5:
                            articles.append({
                                'url': href,
                                'title': title.strip(),
                                'source': 'google'
                            })
                            print(f"  ✓ {title[:60]}...")
                            
                            if len(articles) >= max_results:
                                break
                
                except:
                    continue
            
            print(f"✓ Scraped {len(articles)} articles\n")
            
        except Exception as e:
            print(f"✗ Error: {e}\n")
        
        return articles
    
    def scrape_youtube(self, topic, max_results=10):
        """
        Scrape YouTube playlists
        """
        print(f"Scraping YouTube for: {topic}")
        playlists = []
        
        try:
            self.driver.get("https://www.youtube.com/")
            time.sleep(3)
            
            # Handle consent
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                for button in buttons:
                    text = button.text.lower()
                    if 'accept' in text or 'agree' in text:
                        button.click()
                        time.sleep(1)
                        break
            except:
                pass
            
            # Search
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            search_box.clear()
            search_box.send_keys(f"{topic} playlist")
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(5)
            
            # Scroll to load more
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1)
            
            # Get playlist links
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            seen = set()
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    
                    if href and 'list=' in href and href not in seen:
                        clean_url = href.split('&')[0]
                        
                        if clean_url not in seen:
                            seen.add(clean_url)
                            
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
            
            print(f"✓ Scraped {len(playlists)} playlists\n")
            
        except Exception as e:
            print(f"✗ Error: {e}\n")
        
        return playlists
    
    def scrape_stackoverflow(self, topic, max_results=10):
        """
        Scrape Stack Overflow - WORKS because undetected!
        """
        print(f"Scraping Stack Overflow for: {topic}")
        questions = []
        
        try:
            # Go to Stack Overflow search
            search_url = f"https://stackoverflow.com/search?q={topic.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(4)
            
            # Scroll to load content
            self.driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(2)
            
            # Get all question links
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    
                    if href and '/questions/' in href and href not in [q['url'] for q in questions]:
                        title = link.text.strip()
                        
                        if title and len(title) > 10:
                            # Try to get vote count
                            try:
                                parent = link.find_element(By.XPATH, './ancestor::div[contains(@class, "s-post-summary")]')
                                vote_elem = parent.find_element(By.CSS_SELECTOR, 'span.s-post-summary--stats-item-number')
                                votes = vote_elem.text
                            except:
                                votes = "0"
                            
                            questions.append({
                                'title': title,
                                'url': href if href.startswith('http') else f"https://stackoverflow.com{href}",
                                'votes': votes,
                                'source': 'stackoverflow'
                            })
                            
                            print(f"  ✓ {title[:60]}... ({votes} votes)")
                            
                            if len(questions) >= max_results:
                                break
                
                except:
                    continue
            
            print(f"✓ Scraped {len(questions)} questions\n")
            
        except Exception as e:
            print(f"✗ Error: {e}\n")
        
        return questions
    
    def scrape_all(self, topic):
        """Scrape everything"""
        print(f"\n{'='*60}")
        print(f"Scraping all content for: {topic}")
        print(f"Using UNDETECTED scraper (bypasses anti-bot)")
        print(f"{'='*60}\n")
        
        results = {
            'topic': topic,
            'articles': self.scrape_google(topic, 10),
            'playlists': self.scrape_youtube(topic, 10),
            'questions': self.scrape_stackoverflow(topic, 10),
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        total = len(results['articles']) + len(results['playlists']) + len(results['questions'])
        
        print(f"{'='*60}")
        print(f"FINAL SUMMARY:")
        print(f"  Articles: {len(results['articles'])}")
        print(f"  Playlists: {len(results['playlists'])}")
        print(f"  Questions: {len(results['questions'])}")
        print(f"  TOTAL: {total}")
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
        f.write(f"# {results['topic']} Articles (Google)\n")
        f.write(f"# Scraped: {results['scraped_at']}\n")
        f.write(f"# Total: {len(results['articles'])}\n\n")
        
        for article in results['articles']:
            f.write(f"{article['url']}\n")
            f.write(f"  Title: {article['title']}\n\n")
    
    # Playlists
    with open('../Videos/playlist.txt', 'w', encoding='utf-8') as f:
        f.write(f"# {results['topic']} Playlists (YouTube)\n")
        f.write(f"# Scraped: {results['scraped_at']}\n")
        f.write(f"# Total: {len(results['playlists'])}\n\n")
        
        for playlist in results['playlists']:
            f.write(f"{playlist['url']}\n")
            f.write(f"  Title: {playlist['title']}\n\n")
    
    # Questions
    with open('../Answers/answers.txt', 'w', encoding='utf-8') as f:
        f.write(f"# {results['topic']} Q&A (Stack Overflow)\n")
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
    print("UNDETECTED SCRAPER - Bypasses All Anti-Bot Detection")
    print("="*60)
    print("Works on: Google, Stack Overflow, YouTube, etc.")
    print("100% FREE - No API keys needed!")
    print("="*60 + "\n")
    
    # Get topic
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter topic: ").strip() or "Python"
    
    scraper = None
    try:
        scraper = UndetectedScraper(headless=False)
        results = scraper.scrape_all(topic)
        
        total = len(results['articles']) + len(results['playlists']) + len(results['questions'])
        
        if total > 0:
            save_results(results)
            print(f"✓ SUCCESS! Scraped {total} items total.")
        else:
            print("✗ WARNING: No data scraped.")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scraper:
            scraper.close()
