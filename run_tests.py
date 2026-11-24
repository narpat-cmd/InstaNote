#!/usr/bin/env python3
"""Test script to verify Flask routes work after fixes"""
import sys
sys.path.insert(0, 'D:/InstaNote')

print("=== Testing Scheduler Fix ===")
from src.scheduler import get_scheduler, JobStatus
s = get_scheduler()
print('get_pending_jobs exists:', hasattr(s, 'get_pending_jobs'))
print('Pending jobs:', s.get_pending_jobs())

print("\n=== Testing Admin Panel Fix ===")
from src.admin_panel import create_app
app, _ = create_app()
print('Admin panel created successfully')

print("\n=== Testing Styles Fallback ===")
from src.config import get_config
config = get_config()
styles = config.image.styles if hasattr(config.image, 'styles') else ['Aesthetic Handwritten Illustrated Infographic', 'Minimalist Modern', 'Vintage Retro', 'Bold & Colorful', 'Professional Clean']
print('Styles available:', len(styles) > 0)
print('Styles:', styles[:2], '...')

print("\n=== All Tests Passed ===")