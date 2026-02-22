"""
RAG Chat Integration - Using Grok AI for content-based Q&A
"""
import os
import requests
from django.utils import timezone
from .models import StudySession


class RAGChatIntegration:
    """Integrate with Grok AI for content-based Q&A"""
    
    def __init__(self):
        self.api_key = os.environ.get('XAI_API_KEY')  # Grok AI API key
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.model = "grok-beta"
        self.timeout = 30  # seconds
    
    @classmethod
    def send_query(cls, session_id: int, query: str, context: str = None) -> dict:
        """
        Send query to Grok AI with content context
        
        Args:
            session_id: StudySession ID
            query: User's question
            context: Optional additional context
            
        Returns:
            dict with response from Grok AI
        """
        try:
            session = StudySession.objects.get(id=session_id)
        except StudySession.DoesNotExist:
            return {'error': 'Session not found'}
        
        # Get content from session
        content_text = session.content.transcript if session.content else ""
        
        # Use provided context or content transcript
        full_context = context or content_text[:5000]  # Limit context size
        
        try:
            # Create instance to access instance variables
            instance = cls()
            
            if not instance.api_key:
                return {
                    'error': 'XAI_API_KEY not configured',
                    'fallback_response': 'Chat service is not configured. Please set up your Grok AI API key.'
                }
            
            # Prepare prompt with context
            system_prompt = """You are an intelligent tutor helping students understand their study material. 
Answer questions based on the provided content context. Be clear, concise, and educational.
If the question is not related to the content, politely redirect the student to focus on the study material."""
            
            user_prompt = f"""Content Context:
{full_context}

Student Question: {query}

Please provide a helpful answer based on the content above."""
            
            # Call Grok AI API
            response = requests.post(
                instance.api_url,
                headers={
                    "Authorization": f"Bearer {instance.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": instance.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=instance.timeout
            )
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            answer = result['choices'][0]['message']['content']
            
            # Record interaction
            cls.record_chat_interaction(session_id, query, answer)
            
            return {
                'success': True,
                'response': answer,
                'sources': ['Grok AI'],
                'confidence': 0.9
            }
        
        except requests.exceptions.ConnectionError:
            return {
                'error': 'Grok AI API not available',
                'message': 'Could not connect to Grok AI. Please check your internet connection.',
                'fallback_response': 'I apologize, but I cannot answer your question right now. The chat service is temporarily unavailable.'
            }
        
        except requests.exceptions.Timeout:
            return {
                'error': 'Request timeout',
                'message': 'Grok AI took too long to respond',
                'fallback_response': 'Your question is taking longer than expected to process. Please try again.'
            }
        
        except Exception as e:
            return {
                'error': f'Grok AI query failed: {str(e)}',
                'fallback_response': 'I encountered an error processing your question. Please try rephrasing it.'
            }
    
    @classmethod
    def record_chat_interaction(cls, session_id: int, query: str, response: str) -> dict:
        """
        Record chat usage as engagement event
        
        Args:
            session_id: StudySession ID
            query: User's question
            response: RAG backend response
            
        Returns:
            dict with success status
        """
        try:
            from .monitoring_collector import MonitoringCollector
            
            # Record as monitoring event
            result = MonitoringCollector.record_event(
                session_id,
                'chat_query',
                {
                    'query': query[:200],  # Limit stored query length
                    'response_length': len(response),
                    'timestamp': str(timezone.now())
                }
            )
            
            return result
        
        except Exception as e:
            return {'error': f'Failed to record interaction: {str(e)}'}
    
    @classmethod
    def get_chat_history(cls, session_id: int) -> dict:
        """
        Get chat history for a session
        
        Args:
            session_id: StudySession ID
            
        Returns:
            dict with chat history
        """
        try:
            session = StudySession.objects.get(id=session_id)
            metrics = session.metrics
            
            # Extract chat events from content_interactions
            chat_count = metrics.chat_queries_count
            
            return {
                'success': True,
                'session_id': session_id,
                'total_queries': chat_count,
                'message': 'Chat history tracking is active'
            }
        
        except Exception as e:
            return {'error': f'Failed to get chat history: {str(e)}'}
