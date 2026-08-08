import json
import sys
import os

# Add the current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

def export_openapi():
    openapi_schema = app.openapi()
    with open("venturetwin_openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print("Exported openapi.json successfully.")

if __name__ == "__main__":
    export_openapi()
