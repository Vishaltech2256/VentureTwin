"""
VentureTwin ML Package
----------------------
Standalone machine learning and what-if simulation service for VentureTwin.
Predicts relative startup success likelihood based on capital raised, industry sector,
and geographic hub, while clearly distinguishing deterministic financial calculations
from machine learning inference.

Key APIs:
- predict_startup(input_dict: dict) -> dict
- simulate_whatif(base_input: dict, changes: dict) -> dict
"""

from .service import predict_startup, simulate_whatif

__all__ = ["predict_startup", "simulate_whatif"]
