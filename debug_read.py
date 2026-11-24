#!/usr/bin/env python3
"""Debug script to read specific lines from files"""

def read_lines(filepath, start, end):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    for i in range(start, min(end, len(lines))):
        print(f'{i+1}: {lines[i].rstrip()}')

print("=== admin_panel.py lines 259-310 ===")
read_lines('src/admin_panel.py', 258, 310)

print("\n=== generate.html lines 146-175 ===")
read_lines('templates/generate.html', 145, 175)

print("\n=== settings.html lines 346-410 ===")
read_lines('templates/settings.html', 345, 410)