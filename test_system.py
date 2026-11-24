#!/usr/bin/env python3
"""Test script for InstaNote"""

import sys
sys.path.insert(0, '.')

print("=" * 60)
print("InstaNote System Test")
print("=" * 60)

# Test 1: Config
print("\n[1] Testing Config...")
try:
    from src.config import load_config, get_config
    config = load_config()
    print("    ✅ Config loaded successfully")
except Exception as e:
    print(f"    ❌ Config error: {e}")

# Test 2: Topic Selector
print("\n[2] Testing Topic Selector...")
try:
    from src.topic_selector import select_random_topic, load_published_topics
    topic_data = select_random_topic()
    print(f"    ✅ Topic selected: {topic_data.get('vehicle', 'Unknown')} (Category: {topic_data.get('category', 'Unknown')})")
except Exception as e:
    print(f"    ❌ Topic selector error: {e}")

# Test 3: Researcher
print("\n[3] Testing Researcher...")
try:
    from src.researcher import research_vehicle
    print("    ✅ Researcher module loaded")
except Exception as e:
    print(f"    ❌ Researcher error: {e}")

# Test 4: Content Generator
print("\n[4] Testing Content Generator...")
try:
    from src.content_generator import InfographicGenerator
    gen = InfographicGenerator()
    print("    ✅ Content generator initialized")
except Exception as e:
    print(f"    ❌ Content generator error: {e}")

# Test 5: Instagram Poster
print("\n[5] Testing Instagram Poster...")
try:
    from src.instagram_poster import InstagramPoster
    poster = InstagramPoster()
    print("    ✅ Instagram poster initialized")
except Exception as e:
    print(f"    ❌ Instagram poster error: {e}")

# Test 6: Scheduler
print("\n[6] Testing Scheduler...")
try:
    from src.scheduler import Scheduler
    scheduler = Scheduler()
    print("    ✅ Scheduler initialized")
except Exception as e:
    print(f"    ❌ Scheduler error: {e}")

# Test 7: Admin Panel
print("\n[7] Testing Admin Panel...")
try:
    from src.admin_panel import create_app
    app = create_app()
    print("    ✅ Admin panel Flask app created")
except Exception as e:
    print(f"    ❌ Admin panel error: {e}")

# Test 8: Full Automation Cycle
print("\n[8] Testing Full Automation Cycle...")
try:
    from src.topic_selector import select_random_topic
    from src.researcher import research_vehicle
    from src.content_generator import InfographicGenerator
    from src.utils import ensure_directories
    
    ensure_directories()
    topic_data = select_random_topic()
    topic = topic_data.get('vehicle', 'Unknown')
    print(f"    Selected topic: {topic}")
    
    # Research (mock)
    vehicle_data = {
        'name': topic,
        'manufacturer': 'Test Manufacturer',
        'launch_year': 2025,
        'engine': '3.0L Turbo',
        'horsepower': '350 hp',
        'torque': '350 lb-ft',
        'dimensions': {'length': '4.5m', 'width': '1.8m', 'height': '1.4m'},
        'weight': '1500 kg',
        'transmission': '8-speed automatic',
        'suspension': 'Independent double-wishbone',
        'brakes': 'Ventilated discs with ABS',
        'fuel_tank': '60 L',
        'battery': 'N/A',
        'tyres': '235/45 R18',
        'features': ['LED headlights', 'Touchscreen infotainment', 'Cruise control'],
        'price': '$50,000',
        'colors': ['Red', 'Black', 'White'],
        'advantages': ['Powerful engine', 'Luxury interior'],
        'disadvantages': ['High fuel consumption'],
        'interesting_facts': ['First car with turbo technology']
    }
    
    # Generate image
    gen = InfographicGenerator()
    img = gen.create_image(vehicle_data)
    img.save(f"test_{topic.replace(' ', '_')}.png")
    print(f"    ✅ Image generated: test_{topic.replace(' ', '_')}.png")
except Exception as e:
    print(f"    ❌ Automation cycle error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)