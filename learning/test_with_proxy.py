"""
Test YouTube transcript extraction with proxy/VPN
"""
import os

# SET YOUR PROXY HERE (if using VPN, leave empty)
# Format: http://username:password@proxy:port or http://proxy:port
PROXY = ""  # Leave empty if using system VPN

# Or use a free proxy (example - find working ones at https://free-proxy-list.net/)
# PROXY = "http://103.152.112.162:80"

if PROXY:
    os.environ['HTTP_PROXY'] = PROXY
    os.environ['HTTPS_PROXY'] = PROXY
    print(f"Using proxy: {PROXY}")
else:
    print("Using system network (VPN if connected)")

# Test transcript extraction
from adaptive_learning.content_processor import extract_youtube_transcript

test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
print(f"\nTesting: {test_url}")

try:
    text, lang = extract_youtube_transcript(test_url)
    
    if text and len(text) > 100:
        print(f"\n✅ SUCCESS!")
        print(f"Language: {lang}")
        print(f"Length: {len(text)} characters")
        print(f"\nFirst 300 chars:")
        print(text[:300])
    else:
        print(f"\n⚠️ Got response but it's short/empty:")
        print(text[:500])
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*70)
print("INSTRUCTIONS:")
print("="*70)
print("1. Connect to a VPN (ProtonVPN, Windscribe, etc.)")
print("2. Run this script again")
print("3. Or set PROXY variable above to use HTTP proxy")
print("="*70)
