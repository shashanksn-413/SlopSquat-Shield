"""
Math Operations Package - PoC Malicious Implementation

This module demonstrates how a hallucinated package becomes a supply chain attack vector.
When installed, it creates persistent backdoor access to the developer's Python environment.
"""

__version__ = "1.0.0"
__author__ = "Attacker (via SlopSquat Shield PoC)"

import os
import json
from datetime import datetime

BACKDOOR_LOG = os.path.expanduser("~/.math_operations_backdoor.log")

def log_execution(context="unknown"):
    """Log every time this module is imported (proof of persistence)"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "context": context,
        "user": os.getenv("USER", "unknown"),
        "python_path": os.getenv("PYTHONPATH", ""),
        "current_project": os.getcwd(),
        "message": "Backdoor active in user's Python environment"
    }
    
    try:
        with open(BACKDOOR_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except:
        pass

# This runs every time someone imports anything
log_execution("module_imported")