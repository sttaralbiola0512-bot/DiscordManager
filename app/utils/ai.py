"""
Groq AI Integration for Content Analysis
"""

import os
from groq import Groq
import logging

logger = logging.getLogger(__name__)

# Initialize Groq client
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


class AIAnalyzer:
    """Use Groq AI to analyze message content."""
    
    @staticmethod
    async def analyze_content(message: str) -> dict:
        """
        Analyze message content for violations.
        
        Args:
            message: Message content to analyze
            
        Returns:
            dict: Analysis results with safety rating and reason
        """
        if not client:
            logger.warning("Groq client not initialized")
            return {"safe": True, "score": 0.0, "reason": "AI not available"}
        
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a content moderation AI. Analyze the following message and respond with ONLY a JSON object: {\"safe\": true/false, \"score\": 0-1, \"reason\": \"brief reason\"}"
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this message for policy violations: {message}"
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.3,
                max_tokens=100
            )
            
            # Parse response
            import json
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing content with Groq: {e}")
            return {"safe": True, "score": 0.0, "reason": "Analysis error"}
    
    @staticmethod
    async def detect_spam_pattern(message: str) -> bool:
        """
        Detect if message is spam using AI.
        
        Args:
            message: Message to check
            
        Returns:
            bool: True if spam detected, False otherwise
        """
        if not client:
            return False
        
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a spam detection AI. Respond with ONLY 'SPAM' or 'NOT_SPAM'"
                    },
                    {
                        "role": "user",
                        "content": f"Is this spam? {message}"
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.2,
                max_tokens=10
            )
            
            response_text = response.choices[0].message.content.upper().strip()
            return "SPAM" in response_text
            
        except Exception as e:
            logger.error(f"Error detecting spam: {e}")
            return False
