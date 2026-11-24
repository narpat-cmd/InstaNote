"""Scheduler module for InstaNote - handles automation"""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
import threading
import time
from enum import Enum

HISTORY_FILE = Path(__file__).parent.parent / "data" / "scheduler_state.json"


class JobStatus(Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InstaNoteScheduler:
    """Main scheduler class for InstaNote automation"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.scheduler = Scheduler()
        self._jobs: Dict[str, dict] = {}
    
    def add_job(self, job_id: str, func, schedule: str, **kwargs):
        """Add a scheduled job"""
        self._jobs[job_id] = {
            'func': func,
            'schedule': schedule,
            'kwargs': kwargs,
            'status': JobStatus.PENDING
        }
    
    def get_job(self, job_id: str) -> Optional[dict]:
        """Get job by ID"""
        return self._jobs.get(job_id)
    
    def cancel_job(self, job_id: str):
        """Cancel a job"""
        if job_id in self._jobs:
            self._jobs[job_id]['status'] = JobStatus.CANCELLED
    
    def get_all_jobs(self) -> Dict[str, dict]:
        """Get all jobs"""
        return self._jobs.copy()
    
    def get_stats(self) -> Dict:
        """Get scheduler statistics for dashboard"""
        return {
            'total_jobs': len(self._jobs),
            'pending_jobs': sum(1 for j in self._jobs.values() if j['status'] == JobStatus.PENDING),
            'running_jobs': sum(1 for j in self._jobs.values() if j['status'] == JobStatus.RUNNING),
            'completed_jobs': sum(1 for j in self._jobs.values() if j['status'] == JobStatus.COMPLETED),
            'failed_jobs': sum(1 for j in self._jobs.values() if j['status'] == JobStatus.FAILED),
        }
    
    def get_recent_history(self, limit: int = 10) -> list:
        """Get recent job history for dashboard"""
        history = []
        for job_id, job_data in self._jobs.items():
            entry = {
                'job_id': job_id,
                'schedule': job_data.get('schedule', 'unknown'),
                'status': job_data.get('status', JobStatus.PENDING).value,
                'created_at': job_data.get('created_at', 'unknown')
            }
            history.append(entry)
        # Sort by created_at descending and return top 'limit' entries
        history.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return history[:limit]


def get_scheduler() -> InstaNoteScheduler:
    """Get the singleton scheduler instance"""
    return InstaNoteScheduler()


class Scheduler:
    """Handles automated posting schedule"""
    
    def __init__(self):
        self.running = False
        self.daily_limit = 1
        self.schedule_time = "09:00"
        self.posts_today = 0
        self.last_reset = datetime.now().date()
        self._lock = threading.Lock()
        self._load_state()
    
    def _load_state(self):
        """Load scheduler state from file"""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                data = json.load(f)
                self.daily_limit = data.get('daily_limit', 1)
                self.schedule_time = data.get('schedule_time', '09:00')
                self.last_reset = datetime.fromisoformat(data.get('last_reset', datetime.now().isoformat())).date()
                self.posts_today = data.get('posts_today', 0)
    
    def _save_state(self):
        """Save scheduler state to file"""
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, 'w') as f:
            json.dump({
                'daily_limit': self.daily_limit,
                'schedule_time': self.schedule_time,
                'last_reset': datetime.now().isoformat(),
                'posts_today': self.posts_today,
                'running': self.running
            }, f, indent=2)
    
    def set_daily_limit(self, limit: int):
        """Set daily posting limit"""
        with self._lock:
            self.daily_limit = limit
            self._save_state()
    
    def set_schedule_time(self, time_str: str):
        """Set scheduled posting time (HH:MM format)"""
        with self._lock:
            self.schedule_time = time_str
            self._save_state()
    
    def can_post(self) -> bool:
        """Check if we can post (within daily limit)"""
        with self._lock:
            # Reset counter if new day
            today = datetime.now().date()
            if today > self.last_reset:
                self.posts_today = 0
                self.last_reset = today
            
            return self.posts_today < self.daily_limit and self.running
    
    def increment_post_count(self):
        """Increment post counter"""
        with self._lock:
            self.posts_today += 1
            self._save_state()
    
    def start(self):
        """Start the scheduler"""
        self.running = True
        self._save_state()
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        self._save_state()
    
    def get_status(self) -> Dict:
        """Get scheduler status"""
        with self._lock:
            today = datetime.now().date()
            if today > self.last_reset:
                reset_posts = 0
            else:
                reset_posts = self.posts_today
            
            return {
                'running': self.running,
                'daily_limit': self.daily_limit,
                'posts_today': reset_posts,
                'schedule_time': self.schedule_time,
                'next_post_time': self._calculate_next_post()
            }
    
    def _calculate_next_post(self) -> Optional[str]:
        """Calculate next scheduled post time"""
        if not self.running:
            return None
        
        now = datetime.now()
        hour, minute = map(int, self.schedule_time.split(':'))
        
        next_post = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_post <= now:
            next_post += timedelta(days=1)
        
        return next_post.isoformat()


def run_automation_cycle():
    """Run a complete automation cycle"""
    from .topic_selector import select_random_topic, save_topic
    from .researcher import research_vehicle, generate_caption, generate_hashtags
    from .content_generator import generate_infographic
    from .instagram_poster import post_to_instagram, get_music_for_vehicle
    
    # 1. Select topic
    topic_data = select_random_topic()
    print(f"Selected topic: {topic_data['vehicle']}")
    
    # 2. Research vehicle
    specs = research_vehicle(topic_data['vehicle'])
    print(f"Researched: {specs['name']}")
    
    # 3. Generate infographic
    image_path = generate_infographic(specs)
    print(f"Generated image: {image_path}")
    
    # 4. Prepare caption and hashtags
    caption = generate_caption(specs)
    hashtags = generate_hashtags(specs)
    
    # 5. Post to Instagram
    result = post_to_instagram(image_path, caption, hashtags)
    print(f"Posted: {result.get('permalink', 'Simulated')}")
    
    # 6. Save topic as published
    save_topic(topic_data['category'], topic_data['vehicle'])
    
    return result