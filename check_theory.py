import sys, json
sys.path.insert(0, r'C:\Users\laura\OneDrive\Desktop\python_compass-main!!!!!')
from app import THEORY_EN

# Check for any non-ASCII characters in English content
for key, topic in THEORY_EN.items():
    content = topic['content']
    non_ascii = [c for c in content if ord(c) > 127]
    if non_ascii:
        print(f"{key}: Found {len(non_ascii)} non-ASCII chars: {set(non_ascii)}")
    else:
        print(f"{key}: All ASCII")
