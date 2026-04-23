"""
Path setup for CricView — ensures project root is on sys.path.
Import this at the top of every page file before any other local imports.
"""

import sys
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
