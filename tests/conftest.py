"""
tests/conftest.py – Shared pytest fixtures.
"""

import sys
import os

# Make sure the project root is on the path so that
# 'import cronos.xxx' works without pip-installing first.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
