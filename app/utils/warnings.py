"""
Warning System Management
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class WarningManager:
    """Manage user warnings system."""
    
    MAX_WARNINGS = 3
    WARNING_EXPIRY_DAYS = 7
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Path("data/warnings.json")
        self.db_path.parent.mkdir(exist_ok=True)
        self.warnings = self._load_warnings()
    
    def _load_warnings(self) -> dict:
        """Load warnings from database."""
        try:
            if self.db_path.exists():
                with open(self.db_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading warnings: {e}")
        return {}
    
    def _save_warnings(self):
        """Save warnings to database."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.warnings, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving warnings: {e}")
    
    def add_warning(self, guild_id: str, user_id: str, reason: str, moderator: str) -> int:
        """
        Add warning to user.
        
        Args:
            guild_id: Guild ID
            user_id: User ID
            reason: Warning reason
            moderator: Moderator name
            
        Returns:
            int: Current warning count
        """
        key = f"{guild_id}_{user_id}"
        
        if key not in self.warnings:
            self.warnings[key] = []
        
        warning = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "moderator": moderator
        }
        
        self.warnings[key].append(warning)
        self._save_warnings()
        
        return len(self.warnings[key])
    
    def get_warnings(self, guild_id: str, user_id: str) -> list:
        """
        Get non-expired warnings for user.
        
        Args:
            guild_id: Guild ID
            user_id: User ID
            
        Returns:
            list: List of warnings
        """
        key = f"{guild_id}_{user_id}"
        
        if key not in self.warnings:
            return []
        
        current_time = datetime.now()
        expiry_date = current_time - timedelta(days=self.WARNING_EXPIRY_DAYS)
        
        # Filter non-expired warnings
        self.warnings[key] = [
            w for w in self.warnings[key]
            if datetime.fromisoformat(w['timestamp']) > expiry_date
        ]
        
        self._save_warnings()
        return self.warnings[key]
    
    def clear_warnings(self, guild_id: str, user_id: str):
        """
        Clear all warnings for user.
        
        Args:
            guild_id: Guild ID
            user_id: User ID
        """
        key = f"{guild_id}_{user_id}"
        if key in self.warnings:
            del self.warnings[key]
            self._save_warnings()
            logger.info(f"Cleared warnings for {key}")
