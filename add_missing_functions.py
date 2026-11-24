#!/usr/bin/env python3
"""Add missing functions to content_generator.py"""

# Read the file
with open('src/content_generator.py', 'r') as f:
    content = f.read()

# Add the missing function at the end
if 'def get_content_generator' not in content:
    content += '''

def get_content_generator():
    """Get a content generator instance"""
    return InfographicGenerator()
'''

# Write back
with open('src/content_generator.py', 'w') as f:
    f.write(content)

print("✅ Added get_content_generator function")