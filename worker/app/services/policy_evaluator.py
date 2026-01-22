class PolicyEvaluator:
    def evaluate_tka(self, evidence: dict) -> dict:
        missing = []

        if not evidence.get("diagnosis"):
            missing.append("diagnosis")

        if not evidence.get("imaging_present"):
            missing.append("imaging")

        if not evidence.get("conservative_therapy"):
            missing.append("conservative_therapy")

        if not evidence.get("functional_limitation"):
            missing.append("functional_limitation")

        if missing:
            return {
                "decision": "NEEDS_MORE_INFO",
                "explanation": "Missing required criteria for TKA",
                "missing_requirements": missing,
            }

        return {
            "decision": "APPROVE",
            "explanation": "All medical necessity criteria met",
            "missing_requirements": [],
        }
