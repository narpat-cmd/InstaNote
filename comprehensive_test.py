#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

# Test each import individually
imports = [
    ('src.config', 'get_config'),
    ('src.topic_selector', 'TopicSelector'),
    ('src.scheduler', 'get_scheduler'),
    ('src.content_generator', 'get_content_generator'),
    ('src.instagram_poster', 'get_instagram_poster'),
    ('src.utils', 'setup_logging'),
]

print("Testing imports...")
for module, func in imports:
    try:
        exec(f'from {module} import {func}')
        print(f'✓ {module}.{func}')
    except Exception as e:
        print(f'✗ {module}.{func}: {e}')

print("\nTesting full admin_panel import...")
try:
    from src.admin_panel import create_app
    app, socketio = create_app()
    print('✓ App created successfully')
    print('Routes:', [r.rule for r in app.url_map.iter_rules()])
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()