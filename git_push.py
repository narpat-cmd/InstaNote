#!/usr/bin/env python3
import subprocess
import os

os.chdir('D:/InstaNote')

# Show current status
print("=== Git Status ===")
result = subprocess.run(['git', 'status'], capture_output=True, text=True)
print(result.stdout)

# Show diff for admin_panel.py
print("\n=== Diff for admin_panel.py ===")
result = subprocess.run(['git', 'diff', 'src/admin_panel.py'], capture_output=True, text=True)
print(result.stdout)

# Show diff for scheduler.py
print("\n=== Diff for scheduler.py ===")
result = subprocess.run(['git', 'diff', 'src/scheduler.py'], capture_output=True, text=True)
print(result.stdout)

# Add and commit
print("\n=== Committing changes ===")
result = subprocess.run(['git', 'add', '-A'], capture_output=True, text=True)
print(result.stdout)

commit_msg = 'Fix: Resolve AttributeError in /scheduler and /generate routes'
result = subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

# Push
print("\n=== Pushing to origin ===")
result = subprocess.run(['git', 'push', 'origin', 'master'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)