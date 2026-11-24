"""Utility functions for InstaNote"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def ensure_directories():
    """Create necessary directories"""
    dirs = [
        Path(__file__).parent.parent / "data",
        Path(__file__).parent.parent / "output",
        Path(__file__).parent.parent / "logs"
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def load_json(filepath: Path) -> Dict:
    """Load JSON file"""
    if filepath.exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}


def save_json(filepath: Path, data: Dict):
    """Save JSON file"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().isoformat()


def format_duration(seconds: int) -> str:
    """Format seconds to human readable duration"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"


def setup_logging(level: str = "INFO", log_file: str = None):
    """Setup logging configuration."""
    import logging
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    return logging.getLogger(__name__)


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    
    for unit in units[:-1]:
        if size < 1024.0:
            if unit == 'B':
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"
        size /= 1024.0
    
    return f"{size:.2f} TB"


def time_ago(timestamp) -> str:
    """Calculate time ago from timestamp."""
    from datetime import datetime
    
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)
    
    now = datetime.now()
    diff = now - timestamp
    
    seconds = int(diff.total_seconds())
    
    if seconds < 60:
        return f"{seconds} seconds ago"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days > 1 else ''} ago"


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    import re
    
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    # Remove consecutive hyphens
    text = re.sub(r'-+', '-', text)
    
    return text or 'slug'