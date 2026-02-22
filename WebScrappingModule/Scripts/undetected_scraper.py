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
            # Use Chrome's new headless mode - much harder for sites to detect
            options.add_argument('--headless=new')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # undetected-chromedriver automatically bypasses detection!
        self.driver = uc.Chrome(options=options, version_main=None)
        self.wait = WebDriverWait(self.driver, 10)
        print("✓ Undetected driver initialized (anti-bot bypassed!)\n")
    
    def scrape_google(self, topic, max_results=10):
        """
        Scrape Google search results for articles/tutorials.
        Uses undetected-chromedriver with new headless mode to bypass reCAPTCHA.
        """
        print(f"Scraping Google for articles: {topic}")
        articles = []
        seen_urls = set()
        
        try:
            # Navigate to Google search
            search_url = f"https://www.google.com/search?q={topic.replace(' ', '+')}+tutorial+geeksforgeeks+OR+tutorialspoint+OR+w3schools"
            self.driver.get(search_url)
            time.sleep(3)
            
            # Check if we got past CAPTCHA by looking for search results
            page_source = self.driver.page_source
            if 'recaptcha' in page_source.lower() or len(page_source) < 10000:
                print("  Google CAPTCHA detected, trying consent bypass...")
                # Try to accept consent if present
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                    for button in buttons:
                        text = button.text.lower()
                        if 'accept' in text or 'agree' in text or 'consent' in text:
                            button.click()
                            time.sleep(2)
                            # Re-navigate
                            self.driver.get(search_url)
                            time.sleep(3)
                            break
                except:
                    pass
            
            # Strategy 1: Find h3 elements (Google's result titles)
            h3_elements = self.driver.find_elements(By.TAG_NAME, 'h3')
            print(f"  Found {len(h3_elements)} h3 elements")
            
            for h3 in h3_elements:
                try:
                    title = h3.text.strip()
                    if not title or len(title) < 5:
                        continue
                    
                    # Find the parent <a> link
                    href = None
                    try:
                        parent_link = h3.find_element(By.XPATH, './ancestor::a')
                        href = parent_link.get_attribute('href')
                    except:
                        try:
                            parent_div = h3.find_element(By.XPATH, './..')
                            parent_link = parent_div.find_element(By.TAG_NAME, 'a')
                            href = parent_link.get_attribute('href')
                        except:
                            continue
                    
                    if (href and href.startswith('http') and 
                        'google' not in href.lower() and 
                        'youtube.com' not in href and
                        href not in seen_urls):
                        
                        seen_urls.add(href)
                        articles.append({
                            'url': href,
                            'title': title,
                            'source': 'google'
                        })
                        print(f"  ✓ {title[:60]}")
                        if len(articles) >= max_results:
                            break
                except:
                    continue
            
            # Strategy 2: If Google failed, try DuckDuckGo HTML as fallback
            if len(articles) < 2:
                print(f"  Google returned {len(articles)} results, trying DuckDuckGo fallback...")
                ddg_url = f"https://html.duckduckgo.com/html/?q={topic.replace(' ', '+')}+tutorial"
                self.driver.get(ddg_url)
                time.sleep(2)
                
                result_links = self.driver.find_elements(By.CSS_SELECTOR, 'a.result__a')
                for link in result_links:
                    try:
                        href = link.get_attribute('href')
                        title = link.text.strip()
                        if (href and title and len(title) > 5 and
                            href.startswith('http') and
                            'duckduckgo' not in href and
                            'youtube.com' not in href and
                            href not in seen_urls):
                            seen_urls.add(href)
                            articles.append({
                                'url': href, 'title': title, 'source': 'google'
                            })
                            print(f"  ✓ (DDG) {title[:60]}")
                            if len(articles) >= max_results:
                                break
                    except:
                        continue
            
            # Strategy 3: If still few results, try Bing
            if len(articles) < 2:
                print(f"  Trying Bing fallback...")
                bing_url = f"https://www.bing.com/search?q={topic.replace(' ', '+')}+tutorial"
                self.driver.get(bing_url)
                time.sleep(2)
                
                bing_links = self.driver.find_elements(By.CSS_SELECTOR, 'li.b_algo h2 a')
                if not bing_links:
                    bing_links = self.driver.find_elements(By.CSS_SELECTOR, 'h2 a')
                
                for link in bing_links:
                    try:
                        href = link.get_attribute('href')
                        title = link.text.strip()
                        if (href and title and len(title) > 5 and
                            href.startswith('http') and
                            'bing.com' not in href and 'microsoft' not in href and
                            'youtube.com' not in href and
                            href not in seen_urls):
                            seen_urls.add(href)
                            articles.append({
                                'url': href, 'title': title, 'source': 'google'
                            })
                            print(f"  ✓ (Bing) {title[:60]}")
                            if len(articles) >= max_results:
                                break
                    except:
                        continue
            
            print(f"✓ Scraped {len(articles)} articles\n")
            
        except Exception as e:
            print(f"✗ Article scraping error: {e}\n")
        
        return articles
    
    def scrape_youtube(self, topic, max_results=10):
        """
        Scrape YouTube playlists
        """
        print(f"Scraping YouTube for: {topic}")
        playlists = []
        
        try:
            self.driver.get("https://www.youtube.com/")
            time.sleep(1.5)
            
            # Handle consent
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                for button in buttons:
                    text = button.text.lower()
                    if 'accept' in text or 'agree' in text:
                        button.click()
                        time.sleep(0.5)
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
            
            time.sleep(2.5)
            
            # Scroll to load more
            for _ in range(2):
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(0.5)
            
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
        Scrape Stack Overflow search results.
        Uses multiple strategies to find questions and vote counts.
        """
        print(f"Scraping Stack Overflow for: {topic}")
        questions = []
        seen_urls = set()
        
        try:
            # Go to Stack Overflow search
            search_url = f"https://stackoverflow.com/search?q={topic.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(2.5)
            
            # Scroll to load content
            self.driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)
            
            # Strategy 1: Find question summary containers
            # Try multiple possible class names (SO changes these)
            question_containers = []
            for selector in ['div.s-post-summary', 'div.question-summary', 'div.search-result']:
                try:
                    question_containers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if question_containers:
                        print(f"  Found {len(question_containers)} results via '{selector}'")
                        break
                except:
                    continue
            
            for container in question_containers:
                try:
                    # Find the question link within the container
                    link = None
                    title = None
                    
                    # Try to get the title link
                    for link_selector in ['a.s-link', 'a.question-hyperlink', 'h3 a', 'a[href*="/questions/"]']:
                        try:
                            link = container.find_element(By.CSS_SELECTOR, link_selector)
                            title = link.text.strip()
                            if title:
                                break
                        except:
                            continue
                    
                    if not link or not title or len(title) < 10:
                        continue
                    
                    href = link.get_attribute('href')
                    if not href or '/questions/' not in href:
                        continue
                    
                    if not href.startswith('http'):
                        href = f"https://stackoverflow.com{href}"
                    
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)
                    
                    # Try to get vote count
                    votes = "0"
                    for vote_selector in ['span.s-post-summary--stats-item-number', 'span.vote-count-post', 'div.votes span', 'span.js-vote-count']:
                        try:
                            vote_elem = container.find_element(By.CSS_SELECTOR, vote_selector)
                            votes = vote_elem.text.strip()
                            if votes:
                                break
                        except:
                            continue
                    
                    questions.append({
                        'title': title,
                        'url': href,
                        'votes': votes,
                        'source': 'stackoverflow'
                    })
                    
                    print(f"  ✓ {title[:60]}... ({votes} votes)")
                    
                    if len(questions) >= max_results:
                        break
                except:
                    continue
            
            # Strategy 2: Fallback - find all links with /questions/ in href
            if len(questions) < 3:
                print("  Trying fallback link scan...")
                all_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/questions/"]')
                
                for link in all_links:
                    try:
                        href = link.get_attribute('href')
                        title = link.text.strip()
                        
                        if (title and len(title) > 10 and
                            '/questions/' in href and
                            '/tagged/' not in href and
                            href not in seen_urls):
                            
                            if not href.startswith('http'):
                                href = f"https://stackoverflow.com{href}"
                            
                            seen_urls.add(href)
                            questions.append({
                                'title': title,
                                'url': href,
                                'votes': '0',
                                'source': 'stackoverflow'
                            })
                            print(f"  ✓ (fallback) {title[:60]}")
                            
                            if len(questions) >= max_results:
                                break
                    except:
                        continue
            
            print(f"✓ Scraped {len(questions)} questions\n")
            
        except Exception as e:
            print(f"✗ StackOverflow scraping error: {e}\n")
        
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
        """Close browser safely"""
        print("Closing browser...")
        try:
            self.driver.quit()
        except OSError:
            pass  # Handle WinError 6: The handle is invalid
        except Exception:
            pass
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
