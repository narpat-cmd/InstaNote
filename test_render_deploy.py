#!/usr/bin/env python3
"""Test script to verify all imports work for Render deployment"""
import sys
sys.path.insert(0, '.')

print("Testing all imports for Render deployment...")

errors = []

# Test 1: Core imports
try:
    from src.utils import setup_logging, format_file_size, time_ago, slugify
    print("✓ src.utils imports OK")
except ImportError as e:
    errors.append(f"src.utils: {e}")
    print(f"✗ src.utils import failed: {e}")

# Test 2: Instagram poster
try:
    from src.instagram_poster import get_instagram_poster
    print("✓ src.instagram_poster imports OK")
except ImportError as e:
    errors.append(f"src.instagram_poster: {e}")
    print(f"✗ src.instagram_poster import failed: {e}")

# Test 3: Admin panel (this is what fails on Render)
try:
    from src.admin_panel import create_app
    print("✓ src.admin_panel imports OK")
except ImportError as e:
    errors.append(f"src.admin_panel: {e}")
    print(f"✗ src.admin_panel import failed: {e}")

# Test 4: Config
try:
    from src.config import get_config
    print("✓ src.config imports OK")
except ImportError as e:
    errors.append(f"src.config: {e}")
    print(f"✗ src.config import failed: {e}")

# Test 5: Content generator
try:
    from src.content_generator import get_content_generator
    print("✓ src.content_generator imports OK")
except ImportError as e:
    errors.append(f"src.content_generator: {e}")
    print(f"✗ src.content_generator import failed: {e}")

# Test 6: Researcher
try:
    from src.researcher import get_vehicle_specs
    print("✓ src.researcher imports OK")
except ImportError as e:
    errors.append(f"src.researcher: {e}")
    print(f"✗ src.researcher import failed: {e}")

# Test 7: Topic selector
try:
    from src.topic_selector import select_topic
    print("✓ src.topic_selector imports OK")
except ImportError as e:
    errors.append(f"src.topic_selector: {e}")
    print(f"✗ src.topic_selector import failed: {e}")

# Test 8: Flask app creation
try:
    from src.admin_panel import create_app
    app = create_app()
    print("✓ Flask app created successfully")
except Exception as e:
    errors.append(f"Flask app creation: {e}")
    print(f"✗ Flask app creation failed: {e}")

print("\n" + "="*50)
if errors:
    print("ERRORS FOUND:")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED!")
    sys.exit(0)