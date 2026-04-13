"""
compare_baselines.py — Compare baseline performance to Agentic reasoning.
"""

import os
import sys
import json
from sklearn.model_selection import train_test_split

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from evaluation.metrics import compute_metrics, confidence_calibration_score
from evaluation.explain_eval import evaluate_explanations

def main():
    agent_path = os.path.join(PROJECT_ROOT, "data", "processed", "agent_results.jsonl")
    
    if not os.path.exists(agent_path):
        print("Agent results not found. Run scripts/run_agent.py first.")
        return
        
    true_labels = []
    agent_preds = []
    agent_reports = []
    
    with open(agent_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            d = json.loads(line)
            true_labels.append(d["true_label"])
            report = d["agent_report"]
            agent_preds.append(report["label"])
            agent_reports.append(report)
            
    m = compute_metrics(true_labels, agent_preds)
    calib = confidence_calibration_score(agent_reports, true_labels)
    exp = evaluate_explanations(agent_reports)
    
    print("\n--- AGENTIC MODEL RESULTS ---")
    print(f"Total Samples Tested: {len(true_labels)}")
    print(f"Accuracy:  {m['accuracy']:.4f}")
    print(f"Precision: {m['precision']:.4f}")
    print(f"Recall:    {m['recall']:.4f}")
    print(f"F1 Score:  {m['f1']:.4f}")
    print(f"Valid Explanations: {exp['valid_explanation_rate']*100:.1f}%")
    print("\nConfidence Calibration:")
    print(f"  High Confidence ({calib['high_confidence_count']} cases): {calib['high_confidence_accuracy']:.4f} acc")
    print(f"  Low/Med Confidence ({calib['low_confidence_count']} cases): {calib['low_confidence_accuracy']:.4f} acc")
    print("-----------------------------\n")

if __name__ == "__main__":
    main()
