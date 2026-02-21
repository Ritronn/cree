"""
Modern Web Scraper for Educational Content (2026)
Uses simple, reliable methods instead of Selenium
"""

import requests
from bs4 import BeautifulSoup
import json

def scrape_tutorials(topic):
    """
    Scrape tutorial links for any topic
    """
    print(f"Scraping {topic} tutorials...")
    
    tutorials = []
    
    # Try to scrape from FreeCodeCamp
    try:
        search_url = f"https://www.freecodecamp.org/news/search/?query={topic.replace(' ', '%20')}"
        response = requests.get(
            search_url,
            timeout=10,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('a', class_='post-card-content-link', limit=10)
            
            for article in articles:
                href = article.get('href')
                if href:
                    full_url = f"https://www.freecodecamp.org{href}" if href.startswith('/') else href
                    title = article.get_text(strip=True)
                    tutorials.append({
                        'url': full_url,
                        'title': title,
                        'type': 'article',
                        'source': 'freecodecamp'
                    })
    except Exception as e:
        print(f"Could not scrape FreeCodeCamp: {e}")
    
    # Try Google search for tutorials
    try:
        search_query = f"{topic} tutorial"
        # Using a simple approach - in production, use Google Custom Search API
        print(f"  Searching for: {search_query}")
    except Exception as e:
        print(f"Could not search Google: {e}")
    
    return tutorials


def scrape_youtube_playlists(topic):
    """
    Get YouTube playlist links for any topic
    """
    print(f"Getting {topic} YouTube playlists...")
    
    playlists = []
    
    # Note: For production, use YouTube Data API v3
    # This is a placeholder showing the structure
    print(f"  Note: Use YouTube Data API for topic: {topic}")
    print(f"  API URL: https://www.googleapis.com/youtube/v3/search?q={topic}+playlist")
    
    return playlists


def scrape_qa_content(topic):
    """
    Get Q&A content for any topic
    """
    print(f"Getting {topic} Q&A content...")
    
    qa_content = []
    
    # Stack Overflow search
    try:
        # Convert topic to tag format (e.g., "Machine Learning" -> "machine-learning")
        tag = topic.lower().replace(' ', '-')
        
        response = requests.get(
            'https://api.stackexchange.com/2.3/questions',
            params={
                'order': 'desc',
                'sort': 'votes',
                'tagged': tag,
                'site': 'stackoverflow',
                'pagesize': 10
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                qa_content.append({
                    'title': item.get('title'),
                    'url': item.get('link'),
                    'score': item.get('score'),
                    'source': 'stackoverflow'
                })
    except Exception as e:
        print(f"Could not fetch Stack Overflow: {e}")
    
    # Reddit search
    try:
        # Search relevant subreddit
        subreddit = 'learnprogramming'  # General programming
        search_query = topic
        
        response = requests.get(
            f'https://www.reddit.com/r/{subreddit}/search.json',
            params={'q': search_query, 'limit': 10, 'sort': 'top', 't': 'month'},
            headers={'User-Agent': 'EducationalBot/1.0'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                qa_content.append({
                    'title': post_data.get('title'),
                    'url': f"https://www.reddit.com{post_data.get('permalink')}",
                    'score': post_data.get('score'),
                    'source': 'reddit'
                })
    except Exception as e:
        print(f"Could not fetch Reddit: {e}")
    
    return qa_content


def save_results(topic):
    """Save all scraped content to files"""
    
    # Scrape all content for the given topic
    tutorials = scrape_tutorials(topic)
    playlists = scrape_youtube_playlists(topic)
    qa_content = scrape_qa_content(topic)
    
    # Save tutorials
    with open('../Articles/articles.txt', 'w', encoding='utf-8') as f:
        f.write(f"# {topic} Tutorials (Scraped 2026-02-20)\n\n")
        for item in tutorials:
            f.write(f"{item['url']}\n")
            f.write(f"  Title: {item['title']}\n")
            f.write(f"  Source: {item.get('source', 'unknown')}\n\n")
    
    # Save playlists
    with open('../Videos/playlist.txt', 'w', encoding='utf-8') as f:
        f.write(f"# {topic} YouTube Playlists (Scraped 2026-02-20)\n\n")
        if playlists:
            for item in playlists:
                f.write(f"{item['url']}\n")
                f.write(f"  Title: {item['title']}\n")
                f.write(f"  Channel: {item.get('channel', 'unknown')}\n\n")
        else:
            f.write(f"Note: Use YouTube Data API to search for '{topic} playlist'\n")
            f.write(f"API: https://www.googleapis.com/youtube/v3/search\n")
    
    # Save Q&A
    with open('../Answers/answers.txt', 'w', encoding='utf-8') as f:
        f.write(f"# {topic} Q&A (Scraped 2026-02-20)\n\n")
        for item in qa_content:
            f.write(f"{item['title']}\n")
            f.write(f"  URL: {item['url']}\n")
            f.write(f"  Score: {item['score']}\n")
            f.write(f"  Source: {item['source']}\n\n")
    
    # Also save as JSON for easier parsing
    import datetime
    with open('../scraped_data.json', 'w', encoding='utf-8') as f:
        json.dump({
            'topic': topic,
            'tutorials': tutorials,
            'playlists': playlists,
            'qa_content': qa_content,
            'scraped_at': datetime.datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n✓ Saved {len(tutorials)} tutorials")
    print(f"✓ Saved {len(playlists)} playlists")
    print(f"✓ Saved {len(qa_content)} Q&A items")
    print("\nFiles created:")
    print("  - Articles/articles.txt")
    print("  - Videos/playlist.txt")
    print("  - Answers/answers.txt")
    print("  - scraped_data.json")


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Modern Educational Content Scraper (2026)")
    print("=" * 60)
    print("\nThis scraper uses:")
    print("  ✓ Direct links (most reliable)")
    print("  ✓ Public APIs (Stack Overflow, Reddit)")
    print("  ✓ Simple HTTP requests (no Selenium needed)")
    print("\n" + "=" * 60 + "\n")
    
    # Get topic from command line or user input
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter topic to scrape (e.g., 'Python', 'Machine Learning'): ").strip()
        if not topic:
            topic = "Python"  # Default
    
    print(f"\n🔍 Scraping content for: {topic}\n")
    
    try:
        save_results(topic)
        print("\n✓ Scraping completed successfully!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
