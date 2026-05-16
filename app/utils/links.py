"""
Link Detection Module
"""

import re
import logging

logger = logging.getLogger(__name__)


class LinkDetector:
    """Detect and filter links in messages."""
    
    # Common URL patterns
    URL_PATTERNS = [
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # Full URLs
        r'www\.\S+',  # www. URLs
        r'discord\.gg/\S+',  # Discord invites
        r'bit\.ly/\S+',  # Bit.ly links
    ]
    
    # Whitelist patterns (allowed domains)
    WHITELIST = [
        'github.com',
        'discord.com',
        'documentation.com',
    ]
    
    @staticmethod
    def has_links(message: str) -> bool:
        """
        Check if message contains any links.
        
        Args:
            message: Message content
            
        Returns:
            bool: True if links found
        """
        for pattern in LinkDetector.URL_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def extract_links(message: str) -> list:
        """
        Extract all links from message.
        
        Args:
            message: Message content
            
        Returns:
            list: List of found links
        """
        links = []
        for pattern in LinkDetector.URL_PATTERNS:
            matches = re.findall(pattern, message, re.IGNORECASE)
            links.extend(matches)
        return links
    
    @staticmethod
    def is_whitelisted(url: str) -> bool:
        """
        Check if URL is whitelisted.
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if whitelisted
        """
        for whitelist_domain in LinkDetector.WHITELIST:
            if whitelist_domain in url.lower():
                return True
        return False
