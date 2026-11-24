#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

# Try to import all modules
imports = [
    ('src.config', 'load_config, reload_config'),
    ('src.utils', 'setup_logging, format_file_size, time_ago, slugify'),
    ('src.instagram_poster', 'get_instagram_poster'),
    ('src.topic_selector', 'TopicSelector, VEHICLE_CATEGORIES'),
    ('src.scheduler', 'get_scheduler, InstaNoteScheduler, JobStatus'),
    ('src.content_generator', 'get_content_generator'),
    ('src.researcher', 'research_vehicle, generate_caption, generate_hashtags'),
    ('src.utils', 'ensure_directories'),
    ('src.scheduler', 'run_automation_cycle, Scheduler'),
    ('src.topic_selector', 'select_random_topic, save_topic'),
    ('src.content_generator', 'generate_infographic'),
    ('src.instagram_poster', 'post_to_instagram, get_music_for_vehicle'),
]

for module, funcs in imports:
    try:
        exec(f'from {module} import {funcs}')
        print(f'✓ {module} ({funcs})')
    except Exception as e:
        print(f'✗ {module} ({funcs}): {e}')

print('\nNow testing admin_panel imports...')
try:
    from src.admin_panel import create_app
    print('✓ src.admin_panel')
except Exception as e:
    print(f'✗ src.admin_panel: {e}')
    import traceback
    traceback.print_exc()