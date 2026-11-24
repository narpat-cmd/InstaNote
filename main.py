#!/usr/bin/env python3
"""Main entry point for InstaNote"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils import ensure_directories
from src.scheduler import run_automation_cycle, Scheduler
from src.topic_selector import select_random_topic, save_topic
from src.researcher import research_vehicle, generate_caption, generate_hashtags
from src.content_generator import generate_infographic
from src.instagram_poster import post_to_instagram, get_music_for_vehicle


def main():
    """Main function to run InstaNote automation"""
    print("=" * 50)
    print("InstaNote - Autonomous Instagram Bike/Car Automation")
    print("=" * 50)
    
    # Ensure directories exist
    ensure_directories()
    
    # Initialize scheduler
    scheduler = Scheduler()
    scheduler.start()
    
    print(f"\nScheduler Status: {scheduler.get_status()}")
    
    # Run automation cycle
    try:
        result = run_automation_cycle()
        print(f"\n✅ Post published successfully!")
        print(f"   URL: {result.get('permalink', 'Simulated')}")
        print(f"   Image: {result.get('image_path', 'N/A')}")
        
        # Increment post count
        scheduler.increment_post_count()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())