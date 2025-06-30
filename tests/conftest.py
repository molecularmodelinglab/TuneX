"""
Global test configuration and fixtures.
"""

import os
import sys

# Add the project root to the Python path to allow imports from the 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
