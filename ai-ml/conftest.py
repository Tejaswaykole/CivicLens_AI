"""
Pytest configuration for CivicLens AI AI-ML module.
Ensures src/ is automatically added to sys.path so modules and test files
can cleanly import internal modules without relying on the current working directory.
"""

import sys
from pathlib import Path

# Add ai-ml/src to sys.path
src_path = Path(__file__).resolve().parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
