"""
Spam Detection Module
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SpamDetector:
    """Detect spam messages based on patterns."""
    
    def __init__(self):
        self.user_message_history = defaultdict(list)
        self.spam_threshold = 5  # messages
        self.spam_timeframe = 5  # seconds
    
    def check_spam(self, user_id: int, timestamp: datetime = None) -> bool:
        """
        Check if user is spamming.
        
        Args:
            user_id: Discord user ID
            timestamp: Message timestamp (defaults to now)
            
        Returns:
            bool: True if spam detected
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Add to history
        self.user_message_history[user_id].append(timestamp)
        
        # Clean old messages
        cutoff = timestamp - timedelta(seconds=self.spam_timeframe)
        self.user_message_history[user_id] = [
            t for t in self.user_message_history[user_id]
            if t > cutoff
        ]
        
        # Check threshold
        is_spam = len(self.user_message_history[user_id]) > self.spam_threshold
        
        if is_spam:
            logger.debug(f"Spam detected from user {user_id}")
        
        return is_spam
    
    def check_duplicate(self, user_id: int, message: str, similarity_threshold: float = 0.9) -> bool:
        """
        Check if message is a duplicate of recent messages.
        
        Args:
            user_id: Discord user ID
            message: Message content
            similarity_threshold: How similar messages need to be (0-1)
            
        Returns:
            bool: True if duplicate detected
        """
        message_lower = message.lower().strip()
        
        # Simple duplicate check
        if message_lower in [m.lower().strip() for m in getattr(self, f'user_{user_id}_messages', [])]:
            logger.debug(f"Duplicate message detected from user {user_id}")
            return True
        
        return False
