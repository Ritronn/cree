"""
Content Processing Utilities
Extracts text from YouTube, PDF, PPT, and Word documents
Supports multilingual YouTube videos (Hindi, Marathi, etc.) with auto-translation
"""
import os
import re
from typing import List, Dict, Tuple


# Supported languages for YouTube transcript extraction (priority order)
SUPPORTED_LANGUAGES = ['en', 'hi', 'mr', 'ta', 'te', 'kn', 'ml', 'gu', 'bn', 'pa', 'ur']
LANGUAGE_NAMES = {
    'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi', 'ta': 'Tamil',
    'te': 'Telugu', 'kn': 'Kannada', 'ml': 'Malayalam', 'gu': 'Gujarati',
    'bn': 'Bengali', 'pa': 'Punjabi', 'ur': 'Urdu'
}


def process_content(content):
    """
    Main content processing function
    Extracts text and identifies key concepts
    Handles multilingual YouTube videos with auto-translation to English
    """
    if content.content_type == 'youtube':
        transcript, source_lang = extract_youtube_transcript(content.url)
        content.transcript = transcript
        content.source_language = source_lang
    elif content.content_type == 'pdf':
        content.transcript = extract_pdf_text(content.file.path)
        content.source_language = 'en'
    elif content.content_type == 'ppt':
        content.transcript = extract_ppt_text(content.file.path)
        content.source_language = 'en'
    elif content.content_type == 'word':
        content.transcript = extract_word_text(content.file.path)
        content.source_language = 'en'
    
    # Extract key concepts
    content.key_concepts = extract_key_concepts(content.transcript)
    content.processed = True
    content.save()
    
    return content


def extract_youtube_transcript(url: str) -> Tuple[str, str]:
    """
    Extract transcript from YouTube video with multiple fallback methods.
    
    Returns:
        Tuple of (transcript_text, source_language_code)
    """
    import time
    import random
    
    # Check if it's a playlist
    if 'playlist' in url or 'list=' in url:
        return extract_youtube_playlist_transcript(url)
    
    # Extract video ID from URL
    video_id = extract_video_id(url)
    
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    # Method 1: Try youtube-transcript-api first
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        delay = random.uniform(0.5, 1.5)
        time.sleep(delay)
        
        return _extract_transcript_multilingual(video_id)
    
    except Exception as e:
        error_msg = str(e)
        print(f"[Transcript] youtube-transcript-api failed: {error_msg[:100]}")
        
        # Method 2: Try yt-dlp fallback
        try:
            print(f"[Transcript] Trying yt-dlp fallback...")
            return _extract_transcript_ytdlp(video_id)
        except Exception as e2:
            print(f"[Transcript] yt-dlp also failed: {str(e2)[:100]}")
            
            # Both methods failed - IP is blocked
            error_message = """
            ⚠️ YouTube Transcript Temporarily Unavailable
            
            Your IP has been temporarily blocked by YouTube due to too many automated requests.
            
            SOLUTIONS:
            1. Wait 15-30 minutes for the block to clear
            2. Try a different video
            3. Use a VPN or proxy
            4. Restart your router to get a new IP
            
            This is a temporary YouTube rate limit, not a code issue.
            """
            return error_message.strip(), 'en'


def _extract_transcript_ytdlp(video_id: str) -> Tuple[str, str]:
    """
    Extract transcript using yt-dlp with proxy support.
    
    Returns:
        Tuple of (transcript_text, language_code)
    """
    import yt_dlp
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    # Check for proxy
    proxy = os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY')
    
    # Configure yt-dlp with proxy
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'quiet': True,
        'no_warnings': True,
    }
    
    if proxy:
        print(f"[Transcript] yt-dlp using proxy: {proxy}")
        ydl_opts['proxy'] = proxy
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Get subtitles
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            
            # Try English
            sub_data = subtitles.get('en') or automatic_captions.get('en')
            
            if not sub_data:
                raise ValueError("No English subtitles found")
            
            # Get subtitle URL (prefer vtt or srv3 format)
            sub_url = None
            for fmt in sub_data:
                if fmt.get('ext') in ['vtt', 'srv3', 'srv2', 'srv1']:
                    sub_url = fmt['url']
                    break
            
            if not sub_url and sub_data:
                sub_url = sub_data[0]['url']
            
            if not sub_url:
                raise ValueError("No subtitle URL found")
            
            # Download and parse subtitles with proxy
            import requests
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            response = requests.get(sub_url, timeout=10, proxies=proxies)
            content = response.text
            
            # Parse VTT format
            if 'WEBVTT' in content:
                lines = content.split('\n')
                text_parts = []
                for line in lines:
                    line = line.strip()
                    # Skip timestamps and metadata
                    if line and not line.startswith('WEBVTT') and not '-->' in line and not line.isdigit():
                        # Remove HTML tags
                        import re
                        clean_line = re.sub(r'<[^>]+>', '', line)
                        if clean_line:
                            text_parts.append(clean_line)
                
                text = ' '.join(text_parts)
                print(f"[Transcript] yt-dlp extracted transcript ({len(text)} chars)")
                return text, 'en'
            
            # Parse JSON format
            elif content.startswith('{'):
                import json
                data = json.loads(content)
                text_parts = []
                
                # Handle different JSON structures
                if 'events' in data:
                    for event in data['events']:
                        if 'segs' in event:
                            for seg in event['segs']:
                                if 'utf8' in seg:
                                    text_parts.append(seg['utf8'])
                
                text = ' '.join(text_parts)
                if text:
                    print(f"[Transcript] yt-dlp extracted transcript ({len(text)} chars)")
                    return text, 'en'
            
            raise ValueError("Could not parse subtitle format")
    
    except Exception as e:
        raise ValueError(f"yt-dlp extraction failed: {str(e)}")


def _extract_transcript_multilingual(video_id: str) -> Tuple[str, str]:
    """
    Extract transcript from YouTube video with cookie support.
    
    Returns:
        Tuple of (english_transcript, original_language_code)
    """
    from youtube_transcript_api import YouTubeTranscriptApi
    from http.cookiejar import MozillaCookieJar
    import requests
    
    def _snippets_to_text(snippets):
        """Convert transcript snippets to plain text."""
        parts = []
        for s in snippets:
            if isinstance(s, dict):
                parts.append(s.get('text', ''))
            else:
                parts.append(str(s))
        return ' '.join(parts)
    
    # Look for cookies file
    cookies_path = os.path.join(os.path.dirname(__file__), 'youtube_cookies.txt')
    
    # Create session
    session = requests.Session()
    
    # Load cookies if available
    if os.path.exists(cookies_path):
        try:
            cookie_jar = MozillaCookieJar(cookies_path)
            cookie_jar.load(ignore_discard=True, ignore_expires=True)
            session.cookies = cookie_jar
            print(f"[Transcript] Using cookies from {cookies_path}")
        except Exception as e:
            print(f"[Transcript] Could not load cookies: {e}")
    
    # Add headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    
    # Create API instance with session
    try:
        # Pass cookies to the API
        api = YouTubeTranscriptApi()
        # Monkey patch the session
        if hasattr(api, '_session'):
            api._session = session
    except:
        api = YouTubeTranscriptApi()
    
    # Try languages in priority order
    for lang_code in SUPPORTED_LANGUAGES:
        try:
            transcript_list = api.list(video_id)
            transcript = transcript_list.find_transcript([lang_code])
            data = transcript.fetch()
            text = _snippets_to_text(data)
            lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
            print(f"[Transcript] Found {lang_name} transcript for {video_id}")
            return text, lang_code
        except Exception:
            continue
    
    # If no supported language found, try any available
    try:
        transcript_list = api.list(video_id)
        transcript = list(transcript_list)[0]
        data = transcript.fetch()
        text = _snippets_to_text(data)
        print(f"[Transcript] Found transcript for {video_id}")
        return text, transcript.language_code
    except Exception as e:
        raise ValueError(f"No transcripts/captions found: {str(e)}")


def _translate_via_grok(text: str, source_lang: str) -> str:
    """
    Translate text to English using Grok AI API.
    Used as fallback when YouTube auto-translate is not available.
    
    Args:
        text: Text in source language
        source_lang: Source language code (hi, mr, etc.)
    
    Returns:
        Translated English text, or None if translation fails
    """
    try:
        import requests
        
        api_key = os.environ.get('XAI_API_KEY')
        if not api_key:
            print("[Translation] No XAI_API_KEY found, cannot translate via Grok AI")
            return None
        
        lang_name = LANGUAGE_NAMES.get(source_lang, source_lang)
        
        # Limit text to avoid token limits (keep first ~4000 chars for translation, do in chunks if needed)
        max_chunk_size = 4000
        
        if len(text) <= max_chunk_size:
            chunks = [text]
        else:
            # Split into chunks at sentence boundaries
            chunks = []
            current_chunk = ""
            sentences = text.replace('। ', '।\n').replace('. ', '.\n').split('\n')
            for sentence in sentences:
                if len(current_chunk) + len(sentence) < max_chunk_size:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
            if current_chunk:
                chunks.append(current_chunk.strip())
        
        translated_chunks = []
        
        for i, chunk in enumerate(chunks):
            prompt = f"""Translate the following {lang_name} text to English accurately. 
Preserve the original meaning, technical terms, and context. 
Return ONLY the English translation, nothing else.

{lang_name} text:
{chunk}"""
            
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-beta",
                    "messages": [
                        {"role": "system", "content": f"You are an expert {lang_name}-to-English translator. Translate accurately, preserving technical terms and educational context. Return only the translation."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 3000
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            translated_text = result['choices'][0]['message']['content'].strip()
            translated_chunks.append(translated_text)
            print(f"[Translation] Chunk {i+1}/{len(chunks)} translated successfully")
        
        return ' '.join(translated_chunks)
    
    except Exception as e:
        print(f"[Translation] Grok AI translation failed: {e}")
        return None


def extract_youtube_playlist_transcript(url: str) -> Tuple[str, str]:
    """
    Extract transcripts from all videos in a YouTube playlist.
    Supports multilingual videos with auto-translation.
    Uses pytube to get video IDs from playlist without API key.
    
    Returns:
        Tuple of (combined_transcript, primary_source_language)
    """
    try:
        import re
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt_api = YouTubeTranscriptApi()
        
        # Extract playlist ID
        playlist_match = re.search(r'list=([^&]+)', url)
        if not playlist_match:
            raise ValueError("Invalid playlist URL")
        
        playlist_id = playlist_match.group(1)
        
        # Try to extract video IDs using pytube
        try:
            from pytube import Playlist
            
            playlist = Playlist(url)
            video_ids = []
            
            # Extract video IDs from playlist
            for video_url in playlist.video_urls:
                video_id = extract_video_id(video_url)
                if video_id:
                    video_ids.append(video_id)
            
            if not video_ids:
                raise ValueError("No videos found in playlist")
            
            # Extract transcripts from all videos (with multilingual support)
            all_transcripts = []
            successful_count = 0
            failed_count = 0
            detected_languages = []
            
            for video_id in video_ids:
                try:
                    text, lang = _extract_transcript_multilingual(video_id)
                    all_transcripts.append(text)
                    detected_languages.append(lang)
                    successful_count += 1
                except Exception as e:
                    print(f"Failed to get transcript for video {video_id}: {str(e)}")
                    failed_count += 1
                    continue
            
            if not all_transcripts:
                raise ValueError(f"Could not extract transcripts from any videos in playlist. {failed_count} videos failed.")
            
            # Determine primary language
            primary_lang = max(set(detected_languages), key=detected_languages.count) if detected_languages else 'en'
            
            # Combine all transcripts
            combined_transcript = '\n\n--- Next Video ---\n\n'.join(all_transcripts)
            
            # Add summary at the beginning
            lang_name = LANGUAGE_NAMES.get(primary_lang, primary_lang)
            summary = f"Playlist Transcript Summary: {successful_count} videos processed successfully"
            if failed_count > 0:
                summary += f", {failed_count} videos failed"
            if primary_lang != 'en':
                summary += f" (Original language: {lang_name}, auto-translated to English)"
            
            return f"{summary}\n\n{combined_transcript}", primary_lang
        
        except ImportError:
            # Fallback: Try using requests to scrape playlist page
            return extract_playlist_via_scraping(url, playlist_id)
    
    except Exception as e:
        error_msg = f"Playlist extraction failed: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg}", 'en'


def extract_playlist_via_scraping(url: str, playlist_id: str) -> Tuple[str, str]:
    """
    Fallback method to extract playlist videos using web scraping.
    Supports multilingual transcripts.
    
    Returns:
        Tuple of (combined_transcript, primary_source_language)
    """
    try:
        import requests
        import re
        
        # Fetch playlist page
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Extract video IDs using regex
        video_id_pattern = r'"videoId":"([^"]+)"'
        video_ids = list(set(re.findall(video_id_pattern, response.text)))
        
        if not video_ids:
            raise ValueError("No videos found in playlist")
        
        # Limit to first 20 videos to avoid timeout
        video_ids = video_ids[:20]
        
        # Extract transcripts with multilingual support
        all_transcripts = []
        successful_count = 0
        failed_count = 0
        detected_languages = []
        
        for video_id in video_ids:
            try:
                text, lang = _extract_transcript_multilingual(video_id)
                all_transcripts.append(text)
                detected_languages.append(lang)
                successful_count += 1
            except Exception as e:
                failed_count += 1
                continue
        
        if not all_transcripts:
            raise ValueError(f"Could not extract transcripts from any videos. {failed_count} videos failed.")
        
        # Determine primary language
        primary_lang = max(set(detected_languages), key=detected_languages.count) if detected_languages else 'en'
        
        # Combine all transcripts
        combined_transcript = '\n\n--- Next Video ---\n\n'.join(all_transcripts)
        
        # Add summary
        lang_name = LANGUAGE_NAMES.get(primary_lang, primary_lang)
        summary = f"Playlist Transcript Summary: {successful_count} videos processed successfully"
        if failed_count > 0:
            summary += f", {failed_count} videos failed"
        if primary_lang != 'en':
            summary += f" (Original language: {lang_name}, auto-translated to English)"
        
        return f"{summary}\n\n{combined_transcript}", primary_lang
    
    except Exception as e:
        error_msg = f"Playlist scraping failed: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg}. Please try installing pytube: pip install pytube", 'en'


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def extract_pdf_text(file_path: str) -> str:
    """
    Extract text from PDF file with error handling
    """
    try:
        import PyPDF2
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            if len(pdf_reader.pages) == 0:
                raise ValueError("PDF file is empty")
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if not text.strip():
            raise ValueError("No text could be extracted from PDF")
        
        return text.strip()
    
    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        error_msg = f"PDF text extraction failed: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg}. The PDF may be corrupted or image-based."


def extract_ppt_text(file_path: str) -> str:
    """
    Extract text from PowerPoint file with error handling
    """
    try:
        from pptx import Presentation
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PowerPoint file not found: {file_path}")
        
        prs = Presentation(file_path)
        text = ""
        
        for slide_num, slide in enumerate(prs.slides, 1):
            slide_text = f"\n--- Slide {slide_num} ---\n"
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text += shape.text + "\n"
            text += slide_text
        
        if not text.strip():
            raise ValueError("No text could be extracted from PowerPoint")
        
        return text.strip()
    
    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        error_msg = f"PPT text extraction failed: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg}. The file may be corrupted."


def extract_word_text(file_path: str) -> str:
    """
    Extract text from Word document with error handling
    """
    try:
        import docx
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Word document not found: {file_path}")
        
        doc = docx.Document(file_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        
        if not text.strip():
            raise ValueError("No text could be extracted from Word document")
        
        return text.strip()
    
    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        error_msg = f"Word text extraction failed: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg}. The file may be corrupted."


def extract_key_concepts(text: str, max_concepts: int = 10) -> List[str]:
    """
    Extract key concepts from text
    Simple keyword extraction based on frequency and importance
    """
    if not text:
        return []
    
    # Clean text
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
        'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very'
    }
    
    # Split into words
    words = text.split()
    
    # Count word frequency (excluding stop words and short words)
    word_freq = {}
    for word in words:
        if len(word) > 3 and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    # Get top concepts
    concepts = [word for word, freq in sorted_words[:max_concepts]]
    
    return concepts


def identify_concepts_from_questions(questions: List[Dict]) -> List[str]:
    """
    Extract concepts from generated questions
    """
    concepts = set()
    
    for q in questions:
        if 'concept' in q:
            concepts.add(q['concept'])
    
    return list(concepts)
