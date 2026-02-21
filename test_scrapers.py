"""
Quick test script to check if web scrapers can be imported and initialized
"""

import sys
import os

print("=" * 60)
print("Testing Web Scraping Module")
print("=" * 60)

# Add WebScrappingModule to path
sys.path.insert(0, 'WebScrappingModule/Scripts')

print("\n1. Testing imports...")
try:
    from GoogleSearch import GoogleSearchQuestion
    print("   ✓ GoogleSearch imported successfully")
except Exception as e:
    print(f"   ✗ GoogleSearch import failed: {e}")

try:
    from YoutubeSearch import YoutubeSearchPlaylist
    print("   ✓ YoutubeSearch imported successfully")
except Exception as e:
    print(f"   ✗ YoutubeSearch import failed: {e}")

try:
    from QuoraSearch import QuoraSearchQuestion
    print("   ✓ QuoraSearch imported successfully")
except Exception as e:
    print(f"   ✗ QuoraSearch import failed: {e}")

print("\n2. Checking Selenium installation...")
try:
    import selenium
    print(f"   ✓ Selenium version: {selenium.__version__}")
except ImportError:
    print("   ✗ Selenium not installed")
    print("   Install with: pip install selenium")

print("\n3. Checking output directories...")
dirs = ['WebScrappingModule/Articles', 'WebScrappingModule/Videos', 'WebScrappingModule/Answers']
for dir_path in dirs:
    if os.path.exists(dir_path):
        files = os.listdir(dir_path)
        print(f"   ✓ {dir_path} exists ({len(files)} files)")
    else:
        print(f"   ✗ {dir_path} not found")

print("\n4. Checking existing scraped data...")
files_to_check = [
    'WebScrappingModule/Articles/articles.txt',
    'WebScrappingModule/Videos/playlist.txt',
    'WebScrappingModule/Answers/answers.txt'
]
for file_path in files_to_check:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"   ✓ {file_path} ({size} bytes)")
    else:
        print(f"   ✗ {file_path} not found (no data scraped yet)")

print("\n" + "=" * 60)
print("IMPORTANT NOTES:")
print("=" * 60)
print("1. Chrome Driver is REQUIRED to run scrapers")
print("   Download from: https://chromedriver.chromium.org/downloads")
print("\n2. Update driver path in each script:")
print("   - WebScrappingModule/Scripts/article.py")
print("   - WebScrappingModule/Scripts/youtube.py")
print("   - WebScrappingModule/Scripts/quora.py")
print("\n3. These scrapers are NOT integrated with Django")
print("   They run standalone and save to text files")
print("=" * 60)
