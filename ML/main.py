import sys
import os

# Ensure backend directory is in sys.path so app package can be imported
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if os.path.exists(backend_dir) and backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import app instance from app.main
from app.main import app

__all__ = ["app"]
