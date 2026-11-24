#!/usr/bin/env python3
"""Quick test for InstaNote"""

import sys
sys.path.insert(0, '.')

print('Testing imports...')
from src.config import get_config
from src.topic_selector import select_random_topic, TopicSelector, Topic
from src.researcher import research_vehicle
from src.content_generator import InfographicGenerator
from src.instagram_poster import InstagramPoster
from src.scheduler import Scheduler
from src.utils import ensure_directories
from src.admin_panel import create_app

print('All imports successful!')

# Test config
config = get_config()
print(f'Config loaded: {type(config).__name__}')

# Test topic selector
topic = select_random_topic()
print(f'Selected topic: {topic}')

# Test scheduler
scheduler = Scheduler()
print(f'Scheduler status: {scheduler.get_status()}')

# Test content generator
gen = InfographicGenerator()
print('Content generator initialized')

# Test admin panel
app = create_app()
print('Admin panel created')

print('\nAll tests passed!')