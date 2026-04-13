import os
import sys

# Ensure we can import preprocessing
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from preprocessing.parser import extract_features

class Planner:
    """
    The Planner extracts structural and API features from code
    to build focused context for the Executor LLM prompt.
    """
    def __init__(self, max_features: int = 10):
        self.max_features = max_features

    def plan_analysis(self, code: str) -> dict:
        """
        Runs the static parser and creates a feature summary.
        """
        features = extract_features(code)
        
        api_calls = features.get("api_calls", [])
        # Deduplicate and limit
        api_calls = list(dict.fromkeys(api_calls))[:self.max_features]
        
        crypto_keywords = features.get("crypto_keywords", [])
        crypto_keywords = list(dict.fromkeys(crypto_keywords))[:self.max_features]
        
        return {
            "api_calls": ", ".join(api_calls) if api_calls else "None explicitly detected",
            "crypto_keywords": ", ".join(crypto_keywords) if crypto_keywords else "None explicitly detected"
        }
