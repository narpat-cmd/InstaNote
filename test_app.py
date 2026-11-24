#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
try:
    from src.admin_panel import create_app
    app, socketio = create_app()
    print('✓ App created successfully')
    print('Routes:', [r.rule for r in app.url_map.iter_rules()])
except Exception as e:
    print('ERROR:', e)
    import traceback
    traceback.print_exc()