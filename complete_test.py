#!/usr/bin/env python3
"""Complete test for InstaNote system"""

import sys
sys.path.insert(0, '.')

print("=" * 60)
print("InstaNote System Test")
print("=" * 60)

# Test 1: Config
print("\n[1] Testing Config...")
try:
    from src.config import load_config
    config = load_config()
    print("    ✓ Config loaded successfully")
except Exception as e:
    print(f"    ✗ Config error: {e}")

# Test 2: Utils
print("\n[2] Testing Utils...")
try:
    from src.utils import ensure_directories
    ensure_directories()
    print("    ✓ Directories ensured")
except Exception as e:
    print(f"    ✗ Utils error: {e}")

# Test 3: Topic Selector
print("\n[3] Testing Topic Selector...")
try:
    from src.topic_selector import select_random_topic, save_topic
    topic = select_random_topic()
    print(f"    ✓ Topic selected: {topic}")
except Exception as e:
    print(f"    ✗ Topic selector error: {e}")

# Test 4: Researcher
print("\n[4] Testing Researcher...")
try:
    from src.researcher import research_vehicle
    research = research_vehicle("2025 Audi Q6")
    print(f"    ✓ Research completed: {research.get('vehicle_name', 'N/A')}")
except Exception as e:
    print(f"    ✗ Researcher error: {e}")

# Test 5: Content Generator
print("\n[5] Testing Content Generator...")
try:
    from src.content_generator import InfographicGenerator
    gen = InfographicGenerator()
    print("    ✓ Content generator initialized")
except Exception as e:
    print(f"    ✗ Content generator error: {e}")

# Test 6: Instagram Poster
print("\n[6] Testing Instagram Poster...")
try:
    from src.instagram_poster import post_to_instagram, get_music_for_vehicle
    music = get_music_for_vehicle("Audi Q6")
    print(f"    ✓ Music selected: {music}")
except Exception as e:
    print(f"    ✗ Instagram poster error: {e}")

# Test 7: Scheduler
print("\n[7] Testing Scheduler...")
try:
    from src.scheduler import Scheduler
    scheduler = Scheduler()
    scheduler.start()
    status = scheduler.get_status()
    print(f"    ✓ Scheduler started: {status}")
except Exception as e:
    print(f"    ✗ Scheduler error: {e}")

# Test 8: Admin Panel
print("\n[8] Testing Admin Panel...")
try:
    from src.admin_panel import create_app
    app = create_app()
    print("    ✓ Admin panel Flask app created")
except Exception as e:
    print(f"    ✗ Admin panel error: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)