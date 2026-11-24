#!/usr/bin/env python3
"""Test all endpoints to check for errors"""
import sys
sys.path.insert(0, 'D:/InstaNote')

from src.admin_panel import create_app
from src.content_generator import get_content_generator

print("=== Testing Content Generator ===")
cg = get_content_generator()
print(f"Has config attr: {hasattr(cg, 'config')}")
print(f"Has image_config attr: {hasattr(cg, 'image_config')}")

if hasattr(cg, 'image_config'):
    print(f"image_config type: {type(cg.image_config)}")
    print(f"image_config has styles: {hasattr(cg.image_config, 'styles')}")

print("\n=== Testing Admin Panel Routes ===")
app = create_app()
with app.test_client() as client:
    # Test /scheduler
    resp = client.get('/scheduler')
    print(f'/scheduler Status: {resp.status_code}')
    if resp.status_code not in [200, 302]:
        print(f'Error: {resp.data.decode()[:500]}')
    
    # Test /generate
    resp = client.get('/generate')
    print(f'/generate Status: {resp.status_code}')
    if resp.status_code not in [200, 302]:
        print(f'Error: {resp.data.decode()[:500]}')

print("\n=== All tests completed ===")