import sys
import os

# Ensure the backend directory is on the path so imports work correctly in CI
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
