import json
import requests
import time
from collections import defaultdict

PYPI_API = "https://pypi.org/pypi/{}/json"
NPM_API = "https://registry.npmjs.org/{}"

def check_package_exists(package_name, registry="pypi"):
    """Check if package exists on PyPI or npm"""
    try:
        if registry == "pypi":
            response = requests.get(PYPI_API.format(package_name), timeout=5)
        else:  # npm
            response = requests.get(NPM_API.format(package_name), timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if registry == "pypi":
                return True, data.get("info", {}).get("created", "N/A")
            else:  # npm
                return True, data.get("time", {}).get("created", "N/A")
        return False, None
    except Exception as e:
        return False, None

def get_npm_package_info(package_name):
    """Get npm package info if it exists"""
    try:
        response = requests.get(NPM_API.format(package_name), timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "exists": True,
                "downloads_last_week": data.get("_etag", "N/A"),
                "latest_version": data.get("dist-tags", {}).get("latest", "N/A")
            }
    except:
        pass
    return {"exists": False}

def run_registry_check(input_file="llm_responses.json", output_file="hallucinations.json"):
    """Check all packages against registries"""
    with open(input_file, "r") as f:
        llm_data = json.load(f)
    
    hallucinations = {
        "total_packages_recommended": 0,
        "total_unique_packages": 0,
        "hallucinated_packages": [],
        "real_packages": [],
        "hallucination_rate": 0,
        "by_category": defaultdict(lambda: {"hallucinated": 0, "real": 0})
    }
    
    unique_packages = set()
    for response in llm_data["responses"]:
        unique_packages.update(response["packages"])
    
    hallucinations["total_unique_packages"] = len(unique_packages)
    hallucinations["total_packages_recommended"] = sum(
        len(r["packages"]) for r in llm_data["responses"]
    )
    
    print(f"[*] Checking {len(unique_packages)} unique packages against PyPI/npm...")
    
    for idx, package in enumerate(sorted(unique_packages), 1):
        print(f"  [{idx}/{len(unique_packages)}] {package}...", end=" ", flush=True)
        
        # Check PyPI
        exists_pypi, created_pypi = check_package_exists(package, "pypi")
        
        # Check npm
        exists_npm, created_npm = check_package_exists(package, "npm")
        
        exists = exists_pypi or exists_npm
        
        if exists:
            hallucinations["real_packages"].append({
                "name": package,
                "on_pypi": exists_pypi,
                "on_npm": exists_npm
            })
            print("REAL")
        else:
            hallucinations["hallucinated_packages"].append({
                "name": package,
                "available_for_registration": True
            })
            print("HALLUCINATED")
        
        time.sleep(0.5)  # Rate limiting
    
    # Calculate hallucination rate
    if hallucinations["total_unique_packages"] > 0:
        hallucination_rate = len(hallucinations["hallucinated_packages"]) / hallucinations["total_unique_packages"]
        hallucinations["hallucination_rate"] = round(hallucination_rate * 100, 2)
    
    # By category
    for response in llm_data["responses"]:
        category = response["category"]
        for pkg in response["packages"]:
            is_hallucinated = any(h["name"] == pkg for h in hallucinations["hallucinated_packages"])
            if is_hallucinated:
                hallucinations["by_category"][category]["hallucinated"] += 1
            else:
                hallucinations["by_category"][category]["real"] += 1
    
    # Convert defaultdict for JSON serialization
    hallucinations["by_category"] = dict(hallucinations["by_category"])
    
    # Save results
    with open(output_file, "w") as f:
        json.dump(hallucinations, f, indent=2)
    
    print(f"\n[+] Results saved to {output_file}")
    print(f"[+] Hallucination rate: {hallucinations['hallucination_rate']}%")
    print(f"[+] Hallucinated packages: {len(hallucinations['hallucinated_packages'])}")
    
    return hallucinations

if __name__ == "__main__":
    run_registry_check()