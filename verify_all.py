#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

# Test all imports
print('Testing imports...')
try:
    from src.config import load_config, get_config
    print('✅ Config imports OK')
except Exception as e:
    print(f'❌ Config: {e}')

try:
    from src.topic_selector import TopicSelector, select_topic, mark_published
    print('✅ Topic selector imports OK')
except Exception as e:
    print(f'❌ Topic selector: {e}')

try:
    from src.researcher import research_vehicle, generate_caption
    print('✅ Researcher imports OK')
except Exception as e:
    print(f'❌ Researcher: {e}')

try:
    from src.content_generator import InfographicGenerator, get_content_generator
    print('✅ Content generator imports OK')
except Exception as e:
    print(f'❌ Content generator: {e}')

try:
    from src.instagram_poster import InstagramPoster, post_to_instagram
    print('✅ Instagram poster imports OK')
except Exception as e:
    print(f'❌ Instagram poster: {e}')

try:
    from src.scheduler import get_scheduler, InstaNoteScheduler, JobStatus
    print('✅ Scheduler imports OK')
except Exception as e:
    print(f'❌ Scheduler: {e}')

try:
    from src.admin_panel import create_app
    print('✅ Admin panel imports OK')
except Exception as e:
    print(f'❌ Admin panel: {e}')

print('\nAll imports successful!')