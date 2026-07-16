import re
from typing import List, Dict
import models
from sqlalchemy.orm import Session

class AuditEngine:
    """
    Analyzes the security health of the user's vault.
    Checks for password strength, reuse, and generates helpful security alerts.
    """

    @staticmethod
    def check_strength(password: str) -> int:
        """
        Evaluate password strength on a scale of 0 to 100.
        Criteria: Length, Uppercase, Numbers, Special Characters.
        """
        score = 0
        if len(password) >= 8: score += 20
        if len(password) >= 12: score += 10
        if re.search(r"[A-Z]", password): score += 20
        if re.search(r"[a-z]", password): score += 10
        if re.search(r"\d", password): score += 20
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): score += 20
        return score

    @staticmethod
    def analyze_vault(credentials: List[Dict]) -> Dict:
        """
        Performs a full audit on a list of decrypted credentials.
        Returns overall health score and specific alerts.
        """
        if not credentials:
            return {"health_score": 100, "alerts": [], "total_count": 0}

        total_score = 0
        passwords_seen = {} # pwd -> count
        alerts = []
        
        # 1. Check Strength and Count Duplicates
        for cred in credentials:
            pwd = cred["password"]
            strength = AuditEngine.check_strength(pwd)
            total_score += strength
            
            passwords_seen[pwd] = passwords_seen.get(pwd, 0) + 1
            
            if strength < 50:
                alerts.append({
                    "type": "WEAK_PASSWORD",
                    "service": cred["service_name"],
                    "severity": "CRITICAL" if strength < 30 else "WARNING"
                })

        # 2. Identify Reused Passwords
        reused_count = 0
        for cred in credentials:
            if passwords_seen[cred["password"]] > 1:
                reused_count += 1
                alerts.append({
                    "type": "REUSED_PASSWORD",
                    "service": cred["service_name"],
                    "severity": "MEDIUM"
                })

        # 3. Calculate Overall Health
        avg_strength = total_score / len(credentials)
        # Penalize for reuse: deduct 10 points for every reused password, up to 50pts
        reuse_penalty = min(reused_count * 10, 50)
        overall_health = max(0, int(avg_strength - reuse_penalty))

        return {
            "health_score": overall_health,
            "alerts": alerts,
            "stats": {
                "total": len(credentials),
                "reused": reused_count,
                "weak": len([a for a in alerts if a["type"] == "WEAK_PASSWORD"])
            }
        }
