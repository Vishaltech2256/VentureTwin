"""
conftest.py
-----------
Pytest fixtures and configuration for VentureTwin ML Module tests.
Ensures venturetwin_ml is discoverable without requiring manual PYTHONPATH configuration.
"""

import sys
from pathlib import Path

# Add project root to sys.path so 'import venturetwin_ml' works cleanly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
