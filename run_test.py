#!/usr/bin/env python3
import subprocess
import sys

result = subprocess.run([sys.executable, 'test_system.py'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
sys.exit(result.returncode)