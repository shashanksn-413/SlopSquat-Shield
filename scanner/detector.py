import json
import os
import requests
from datetime import datetime, timedelta

class PackageDetector:
    def __init__(self):
        """Initialize detector with hallucination database"""
        self.hallucination_db = self.load_hallucination_db()
        self.pypi_api = "https://pypi.org/pypi/{}/json"
        self.npm_api = "https://registry.npmjs.org/{}"
    
    def load_hallucination_db(self):
        """Load hallucination database from research phase"""
        db_path = os.path.join(os.path.dirname(__file__), "..", "research", "hallucination_db.json")
        
        if os.path.exists(db_path):
            try:
                with open(db_path, "r") as f:
                    return json.load(f)
            except:
                return {"hallucinated_packages": []}
        return {"hallucinated_packages": []}
    
    def check_pypi(self, package_name):
        """Check package on PyPI"""
        try:
            response = requests.get(self.pypi_api.format(package_name), timeout=5)
            if response.status_code == 200:
                data = response.json()
                info = data.get("info", {})
                releases = data.get("releases", {})
                
                return {
                    "exists": True,
                    "registry": "pypi",
                    "name": info.get("name", package_name),
                    "version": info.get("version", "N/A"),
                    "created": info.get("created", "N/A"),
                    "downloads_last_month": 0,
                    "maintainer": info.get("maintainer", "Unknown"),
                    "home_page": info.get("home_page", "N/A"),
                    "num_releases": len(releases)
                }
            return {"exists": False, "registry": "pypi"}
        except Exception as e:
            return {"exists": False, "registry": "pypi", "error": str(e)}
    
    def check_npm(self, package_name):
        """Check package on npm"""
        try:
            response = requests.get(self.npm_api.format(package_name), timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "exists": True,
                    "registry": "npm",
                    "name": data.get("name", package_name),
                    "version": data.get("dist-tags", {}).get("latest", "N/A"),
                    "created": data.get("time", {}).get("created", "N/A"),
                    "maintainers": len(data.get("maintainers", [])),
                    "homepage": data.get("homepage", "N/A"),
                    "description": data.get("description", "N/A")[:100]
                }
            return {"exists": False, "registry": "npm"}
        except Exception as e:
            return {"exists": False, "registry": "npm", "error": str(e)}
    
    def is_in_hallucination_db(self, package_name):
        """Check if package is in hallucination database"""
        hallucinated = self.hallucination_db.get("hallucinated_packages", [])
        return any(pkg["name"].lower() == package_name.lower() for pkg in hallucinated)
    
    def is_recently_created(self, created_date, days=7):
        """Check if package was created recently (within X days)"""
        if created_date == "N/A":
            return None
        try:
            created = datetime.fromisoformat(created_date.replace("Z", "+00:00"))
            threshold = datetime.now(created.tzinfo) - timedelta(days=days)
            return created > threshold
        except:
            return None
    
    def get_risk_score(self, package_name):
        """Calculate risk score (0-100) for a package"""
        score = 0
        flags = []
        
        # Check hallucination database
        if self.is_in_hallucination_db(package_name):
            score += 50
            flags.append("In LLM hallucination database")
        
        # Check PyPI
        pypi_info = self.check_pypi(package_name)
        
        if not pypi_info.get("exists"):
            # Check npm
            npm_info = self.check_npm(package_name)
            
            if not npm_info.get("exists"):
                score += 40
                flags.append("Does not exist on PyPI or npm")
            else:
                # Exists on npm, check for red flags
                if npm_info.get("maintainers", 0) == 1:
                    score += 15
                    flags.append("Single maintainer on npm")
        else:
            # Exists on PyPI, check for red flags
            num_releases = pypi_info.get("num_releases", 0)
            if isinstance(num_releases, int) and num_releases <= 1:
                score += 20
                flags.append("Very few releases on PyPI")
            
            if self.is_recently_created(pypi_info.get("created", "N/A")):
                score += 15
                flags.append("Recently created package (last 7 days)")
            
            downloads = pypi_info.get("downloads_last_month", 0)
            if isinstance(downloads, int) and downloads < 10:
                score += 10
                flags.append("Very low download count")
        
        # Check for suspicious patterns
        if self._is_suspicious_name(package_name):
            score += 10
            flags.append("Suspicious naming pattern")
        
        return min(score, 100), flags
    
    def _is_suspicious_name(self, package_name):
        """Check for suspicious naming patterns"""
        suspicious_patterns = [
            "test", "demo", "temp", "fake", "mock", "admin", "root",
            "system", "security", "password", "secret", "key", "token",
            "config", "settings", "internal", "private"
        ]
        name_lower = package_name.lower()
        return any(pattern in name_lower for pattern in suspicious_patterns)
    
    def analyze_package(self, package_name):
        """Full analysis of a package"""
        result = {
            "package": package_name,
            "timestamp": datetime.now().isoformat(),
            "risk_score": 0,
            "risk_level": "SAFE",
            "flags": [],
            "pypi_info": {},
            "npm_info": {},
            "recommendation": ""
        }
        
        # Get risk score
        score, flags = self.get_risk_score(package_name)
        result["risk_score"] = score
        result["flags"] = flags
        
        # Get registry info
        result["pypi_info"] = self.check_pypi(package_name)
        result["npm_info"] = self.check_npm(package_name)
        
        # Determine risk level
        if score >= 70:
            result["risk_level"] = "DANGEROUS"
            result["recommendation"] = "DO NOT INSTALL. High probability of malicious intent."
        elif score >= 40:
            result["risk_level"] = "SUSPICIOUS"
            result["recommendation"] = "VERIFY before installation. Check maintainer history and recent activity."
        elif score >= 20:
            result["risk_level"] = "CAUTION"
            result["recommendation"] = "REVIEW before installation. Consider using verified alternatives."
        else:
            result["risk_level"] = "SAFE"
            result["recommendation"] = "Likely safe to install. Standard precautions apply."
        
        return result