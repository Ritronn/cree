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
    Extract transcript from YouTube video or playlist.
    Supports multilingual videos (Hindi, Marathi, etc.) with auto-translation to English.
    
    Strategy:
        1. Try English transcript directly
        2. Find Hindi/Marathi/other transcript → auto-translate to English via YouTube
        3. If auto-translate fails → fetch raw transcript and translate via Grok AI
        4. Return error if no captions at all
    
    Returns:
        Tuple of (transcript_text, source_language_code)
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Check if it's a playlist
        if 'playlist' in url or 'list=' in url:
            return extract_youtube_playlist_transcript(url)
        
        # Extract video ID from URL
        video_id = extract_video_id(url)
        
        if not video_id:
            raise ValueError("Invalid YouTube URL")
        
        # Use the smart multilingual extraction
        return _extract_transcript_multilingual(video_id)
    
    except Exception as e:
        error_msg = f"YouTube transcript extraction failed: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg}. Please ensure the video has captions enabled.", 'en'


def _extract_transcript_multilingual(video_id: str) -> Tuple[str, str]:
    """
    Smart multilingual transcript extraction for a single video.
    
    Priority:
        1. English (manual or auto-generated)
        2. Hindi/Marathi/other Indian language → YouTube auto-translate to English
        3. Hindi/Marathi/other → Grok AI translation to English
        4. Any available language → auto-translate to English
    
    Returns:
        Tuple of (english_transcript, original_language_code)
    """
    from youtube_transcript_api import YouTubeTranscriptApi
    
    # New API (v2.x) uses instance-based access
    ytt = YouTubeTranscriptApi()

    def _snippets_to_text(snippets):
        """Convert FetchedTranscript snippets to plain text."""
        parts = []
        for s in snippets:
            # New API returns objects with .text attribute; old returns dicts
            parts.append(s.text if hasattr(s, 'text') else s.get('text', ''))
        return ' '.join(parts)
    
    try:
        # List all available transcripts for the video
        transcript_list = ytt.list(video_id)
        
        # --- Strategy 1: Try English directly ---
        try:
            # Try manually created English transcript first (highest quality)
            transcript = transcript_list.find_manually_created_transcript(['en'])
            data = transcript.fetch()
            text = _snippets_to_text(data)
            print(f"[Transcript] Found manual English transcript for {video_id}")
            return text, 'en'
        except Exception:
            pass
        
        try:
            # Try auto-generated English transcript
            transcript = transcript_list.find_generated_transcript(['en'])
            data = transcript.fetch()
            text = _snippets_to_text(data)
            print(f"[Transcript] Found auto-generated English transcript for {video_id}")
            return text, 'en'
        except Exception:
            pass
        
        # --- Strategy 2: Find Hindi/Marathi/other language → auto-translate to English ---
        non_english_langs = [lang for lang in SUPPORTED_LANGUAGES if lang != 'en']
        
        for lang_code in non_english_langs:
            try:
                transcript = transcript_list.find_transcript([lang_code])
                lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
                print(f"[Transcript] Found {lang_name} transcript for {video_id}, attempting YouTube auto-translate to English...")
                
                try:
                    translated = transcript.translate('en')
                    data = translated.fetch()
                    text = _snippets_to_text(data)
                    print(f"[Transcript] Successfully auto-translated {lang_name} → English for {video_id}")
                    return text, lang_code
                except Exception as translate_err:
                    print(f"[Transcript] YouTube auto-translate failed for {lang_name}: {translate_err}")
                    
                    # Strategy 3: Fetch raw transcript and translate via Grok AI
                    data = transcript.fetch()
                    raw_text = _snippets_to_text(data)
                    
                    translated_text = _translate_via_grok(raw_text, lang_code)
                    if translated_text and not translated_text.startswith('Error:'):
                        print(f"[Transcript] Successfully translated {lang_name} → English via Grok AI for {video_id}")
                        return translated_text, lang_code
                    
                    print(f"[Transcript] Grok translation failed, returning raw {lang_name} text for {video_id}")
                    return raw_text, lang_code
                    
            except Exception:
                continue
        
        # --- Strategy 4: Try any available transcript and translate ---
        try:
            for transcript in transcript_list:
                lang_code = transcript.language_code
                lang_name = transcript.language
                print(f"[Transcript] Trying available transcript: {lang_name} ({lang_code}) for {video_id}")
                
                try:
                    translated = transcript.translate('en')
                    data = translated.fetch()
                    text = _snippets_to_text(data)
                    print(f"[Transcript] Successfully auto-translated {lang_name} → English for {video_id}")
                    return text, lang_code
                except Exception:
                    data = transcript.fetch()
                    raw_text = _snippets_to_text(data)
                    translated_text = _translate_via_grok(raw_text, lang_code)
                    if translated_text and not translated_text.startswith('Error:'):
                        return translated_text, lang_code
                    return raw_text, lang_code
        except Exception:
            pass
        
        raise ValueError("No transcripts/captions found for this video in any language")
    
    except Exception as e:
        error_msg = f"Multilingual transcript extraction failed: {str(e)}"
        print(f"[Transcript] {error_msg}")
        raise


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
