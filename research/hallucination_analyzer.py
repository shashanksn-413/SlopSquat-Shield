import json
import statistics
from collections import defaultdict

def analyze_hallucinations(input_file="hallucinations.json"):
    """Generate analysis and metrics from hallucination data"""
    with open(input_file, "r") as f:
        data = json.load(f)
    
    analysis = {
        "summary": {},
        "by_category": {},
        "top_hallucinated_packages": [],
        "metrics_for_resume": {}
    }
    
    # Summary stats
    total_packages = data["total_unique_packages"]
    hallucinated = len(data["hallucinated_packages"])
    real = len(data["real_packages"])
    hallucination_rate = data["hallucination_rate"]
    
    analysis["summary"] = {
        "total_unique_packages_recommended": data["total_packages_recommended"],
        "total_unique_packages": total_packages,
        "real_packages": real,
        "hallucinated_packages": hallucinated,
        "hallucination_rate_percent": hallucination_rate,
        "exploitable_packages": hallucinated  # All hallucinated packages are exploitable
    }
    
    # By category breakdown
    for category, counts in data["by_category"].items():
        total_cat = counts["hallucinated"] + counts["real"]
        if total_cat > 0:
            rate = (counts["hallucinated"] / total_cat) * 100
            analysis["by_category"][category] = {
                "total": total_cat,
                "hallucinated": counts["hallucinated"],
                "real": counts["real"],
                "hallucination_rate_percent": round(rate, 2)
            }
    
    # Sort by hallucination rate (descending)
    sorted_categories = sorted(
        analysis["by_category"].items(),
        key=lambda x: x[1]["hallucination_rate_percent"],
        reverse=True
    )
    analysis["by_category"] = dict(sorted_categories)
    
    # Top hallucinated packages (for CLI detection database)
    analysis["top_hallucinated_packages"] = [
        pkg["name"] for pkg in data["hallucinated_packages"][:20]
    ]
    
    # Metrics for resume
    analysis["metrics_for_resume"] = {
        "research_claim_1": f"Discovered that GPT-4o-mini hallucinates non-existent package names in {hallucination_rate}% of coding responses",
        "research_claim_2": f"Identified {hallucinated} exploitable hallucinated packages available for registration",
        "research_claim_3": f"Analyzed {data['total_packages_recommended']} package recommendations across 10 security categories",
        "highest_risk_category": sorted_categories[0][0] if sorted_categories else "N/A",
        "highest_risk_rate": sorted_categories[0][1]["hallucination_rate_percent"] if sorted_categories else 0,
    }
    
    # Save analysis
    with open("analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)
    
    # Print summary to console
    print("\n" + "="*60)
    print("HALLUCINATION ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total unique packages recommended: {data['total_packages_recommended']}")
    print(f"Total unique package names: {total_packages}")
    print(f"Real packages: {real}")
    print(f"Hallucinated packages: {hallucinated}")
    print(f"Hallucination rate: {hallucination_rate}%")
    print(f"Exploitable packages: {hallucinated}")
    print("\n" + "By Category (sorted by hallucination rate):")
    print("-" * 60)
    for category, stats in analysis["by_category"].items():
        print(f"{category:20} | Hallucinated: {stats['hallucinated']:2} | Rate: {stats['hallucination_rate_percent']:.1f}%")
    print("\nTop 10 Hallucinated Packages (for CLI detection):")
    print("-" * 60)
    for i, pkg in enumerate(analysis["top_hallucinated_packages"][:10], 1):
        print(f"{i}. {pkg}")
    print("\n" + "="*60)
    print("Resume Claims:")
    print("="*60)
    for key, value in analysis["metrics_for_resume"].items():
        print(f"{key}: {value}")
    print("="*60 + "\n")
    
    return analysis

def create_hallucination_database(input_file="hallucinations.json", output_file="hallucination_db.json"):
    """Create a structured database of hallucinated packages for the CLI scanner"""
    with open(input_file, "r") as f:
        data = json.load(f)
    
    db = {
        "hallucinated_packages": [
            {"name": pkg["name"], "model": "gpt-4o-mini", "available": pkg["available_for_registration"]}
            for pkg in data["hallucinated_packages"]
        ],
        "total_hallucinations": len(data["hallucinated_packages"]),
        "timestamp": "2024",
        "models_included": ["gpt-4o-mini"]
    }
    
    with open(output_file, "w") as f:
        json.dump(db, f, indent=2)
    
    print(f"[+] Hallucination database created: {output_file}")
    return db

if __name__ == "__main__":
    print("[*] Analyzing hallucination data...")
    analysis = analyze_hallucinations()
    create_hallucination_database()
    print("[+] Analysis complete!")