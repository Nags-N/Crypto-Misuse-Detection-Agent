"""
explain_eval.py — Evaluate explanation quality for Agentic models.
"""

def evaluate_explanations(agent_reports: list) -> dict:
    """
    Lightweight heuristic to evaluate explanation quality.
    In a full research pipeline, this would use an LLM-as-a-judge or human scoring.
    """
    valid_explanations = 0
    total = len(agent_reports)
    
    for report in agent_reports:
        findings = report.get("findings", [])
        if not findings:
            continue
            
        exp = findings[-1].get("explanation", "").lower()
        
        # A valid explanation should be non-empty, longer than 15 chars, and not a parsing error
        if len(exp) > 15 and "parsing error" not in exp:
            valid_explanations += 1
            
    return {
        "valid_explanation_rate": round(valid_explanations / total, 4) if total > 0 else 0.0
    }
