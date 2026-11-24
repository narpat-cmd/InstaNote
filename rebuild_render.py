#!/usr/bin/env python3
"""Script to check Render deployment status and verify all fixes"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("INSTANOTE RENDER DEPLOYMENT VERIFICATION")
print("=" * 60)

# Test all imports
print("\n[1] Testing all module imports...")
errors = []

try:
    from src.utils import setup_logging, format_file_size, time_ago, slugify
    print("    ✓ src.utils imports OK")
except ImportError as e:
    errors.append(f"src.utils: {e}")
    print(f"    ✗ src.utils: {e}")

try:
    from src.instagram_poster import get_instagram_poster
    print("    ✓ src.instagram_poster imports OK")
except ImportError as e:
    errors.append(f"src.instagram_poster: {e}")
    print(f"    ✗ src.instagram_poster: {e}")

try:
    from src.admin_panel import create_app
    print("    ✓ src.admin_panel imports OK")
except ImportError as e:
    errors.append(f"src.admin_panel: {e}")
    print(f"    ✗ src.admin_panel: {e}")

try:
    from src.topic_selector import select_topic
    print("    ✓ src.topic_selector imports OK")
except ImportError as e:
    errors.append(f"src.topic_selector: {e}")
    print(f"    ✗ src.topic_selector: {e}")

try:
    from src.content_generator import get_content_generator
    print("    ✓ src.content_generator imports OK")
except ImportError as e:
    errors.append(f"src.content_generator: {e}")
    print(f"    ✗ src.content_generator: {e}")

try:
    from src.researcher import research_vehicle
    print("    ✓ src.researcher imports OK")
except ImportError as e:
    errors.append(f"src.researcher: {e}")
    print(f"    ✗ src.researcher: {e}")

try:
    from src.config import get_config
    print("    ✓ src.config imports OK")
except ImportError as e:
    errors.append(f"src.config: {e}")
    print(f"    ✗ src.config: {e}")

# Test Flask app creation
print("\n[2] Testing Flask app creation...")
try:
    app = create_app()
    print("    ✓ Flask app created successfully")
    print(f"    Routes: {[rule.rule for rule in list(app.url_map.iter_rules())[:5]]}")
except Exception as e:
    errors.append(f"Flask app: {e}")
    print(f"    ✗ Flask app creation failed: {e}")

# Summary
print("\n" + "=" * 60)
if errors:
    print("ERRORS FOUND:")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED!")
    print("\nNEXT STEPS:")
    print("  1. Go to https://dashboard.render.com")
    print("  2. Open InstaNote service")
    print("  3. Click 'Rebuild' button")
    print("  4. Wait for build to complete")
    print("  5. Check https://instanote-lkw6.onrender.com/")
    sys.exit(0)