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