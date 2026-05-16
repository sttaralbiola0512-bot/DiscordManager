"""
Local Database Management
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    """Local JSON database for storing bot data."""
    
    def __init__(self, db_dir: Path = None):
        self.db_dir = db_dir or Path("data")
        self.db_dir.mkdir(exist_ok=True)
        
        # Database files
        self.warnings_db = self.db_dir / "warnings.json"
        self.config_db = self.db_dir / "config.json"
        self.users_db = self.db_dir / "users.json"
    
    def _read_file(self, file_path: Path) -> dict:
        """Read JSON file."""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
        return {}
    
    def _write_file(self, file_path: Path, data: dict):
        """Write JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing {file_path}: {e}")
    
    def save_warning(self, guild_id: str, user_id: str, reason: str, moderator: str):
        """Save warning to database."""
        data = self._read_file(self.warnings_db)
        key = f"{guild_id}_{user_id}"
        
        if key not in data:
            data[key] = []
        
        warning = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "moderator": moderator
        }
        
        data[key].append(warning)
        self._write_file(self.warnings_db, data)
    
    def get_warnings(self, guild_id: str, user_id: str) -> list:
        """Get warnings for user."""
        data = self._read_file(self.warnings_db)
        key = f"{guild_id}_{user_id}"
        return data.get(key, [])
    
    def clear_warnings(self, guild_id: str, user_id: str):
        """Clear warnings for user."""
        data = self._read_file(self.warnings_db)
        key = f"{guild_id}_{user_id}"
        
        if key in data:
            del data[key]
            self._write_file(self.warnings_db, data)
