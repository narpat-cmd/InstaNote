#!/usr/bin/env python3
"""Comprehensive test for both fixes"""
import sys
sys.path.insert(0, 'D:/InstaNote')

print("=== Testing Scheduler ===")
from src.scheduler import get_scheduler, JobStatus
scheduler = get_scheduler()
print(f"Scheduler has get_pending_jobs: {hasattr(scheduler, 'get_pending_jobs')}")
print(f"Scheduler has get_all_jobs: {hasattr(scheduler, 'get_all_jobs')}")

# Test get_pending_jobs
try:
    pending = scheduler.get_pending_jobs()
    print(f"get_pending_jobs() returned: {type(pending)} with {len(pending)} items")
except Exception as e:
    print(f"ERROR in get_pending_jobs: {e}")

# Test get_all_jobs
try:
    all_jobs = scheduler.get_all_jobs()
    print(f"get_all_jobs() returned: {type(all_jobs)} with {len(all_jobs)} items")
except Exception as e:
    print(f"ERROR in get_all_jobs: {e}")

print("\n=== Testing Content Generator ===")
from src.content_generator import get_content_generator
cg = get_content_generator()
print(f"Content generator has config: {hasattr(cg, 'config')}")
print(f"Content generator has image_config: {hasattr(cg, 'image_config')}")

print("\n=== Testing Admin Panel ===")
from src.admin_panel import create_app
try:
    result = create_app()
    print(f"create_app returned: {type(result)}")
    if isinstance(result, tuple):
        app, socketio = result
        print("Successfully unpacked app and socketio")
        # Test routes
        with app.test_client() as client:
            resp = client.get('/scheduler')
            print(f"/scheduler status: {resp.status_code}")
            
            resp = client.get('/generate')
            print(f"/generate status: {resp.status_code}")
    else:
        print("ERROR: create_app did not return a tuple")
except Exception as e:
    print(f"ERROR in create_app: {e}")
    import traceback
    traceback.print_exc()

print("\n=== All tests completed ===")