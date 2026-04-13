"""
run_agent.py — Main entry point to run the Agentic AI approach.
"""

import os
import sys
import json
import logging
import argparse
import time
from tqdm import tqdm

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from agent.agent import CryptoMisuseAgent

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-run", action="store_true", help="Run only the first 10 samples for quick testing")
    parser.add_argument("--dataset", type=str, default="data/processed/dataset.jsonl")
    parser.add_argument("--out", type=str, default="data/processed/agent_results.jsonl")
    parser.add_argument("--quiet", action="store_true", help="Suppress live reasoning output")
    args = parser.parse_args()

    dataset_path = os.path.join(PROJECT_ROOT, args.dataset)
    out_path = os.path.join(PROJECT_ROOT, args.out)

    if not os.path.exists(dataset_path):
        print(f"Dataset not found: {dataset_path}")
        sys.exit(1)

    agent = CryptoMisuseAgent()

    samples = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))

    if args.test_run:
        samples = samples[:2]
        
    print(f"Running Agent on {len(samples)} samples...")
    
    # Overwrite previous results if starting fresh
    if os.path.exists(out_path):
        os.remove(out_path)

    iterator = tqdm(samples) if args.quiet else samples
    
    for i, s in enumerate(iterator):
        report = agent.analyze(s["code_snippet"])
        
        full_result = {
            "metadata": s.get("metadata", {}),
            "true_label": s["label"],
            "agent_report": report.to_dict()
        }
        
        if not args.quiet:
            print("\n" + "="*64)
            name = s.get("metadata", {}).get("name", "Unknown Case")
            print(f"[{i+1}/{len(samples)}] {name}")
            print("-" * 64)
            lines = s['code_snippet'].split('\n')
            snip = '\n'.join(lines[:5]) + ('\n  ...' if len(lines) > 5 else '')
            print(f"CODE (snippet):\n  {snip}\n")
            print(f"AGENT REASONING:\n{report.reasoning_trace}\n")
            
            finding = report.findings[-1] if report.findings else {}
            verdict = finding.get("verdict", "UNKNOWN").upper()
            conf = finding.get("confidence", "UNKNOWN").upper()
            expl = finding.get("explanation", "")
            hint = finding.get("line_hint", "")
            
            print(f"VERDICT: {verdict}  |  Confidence: {conf}")
            print(f"EXPLANATION: {expl}")
            if hint:
                print(f"LINE HINT: {hint}")
            print("="*64 + "\n")
        
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(full_result, ensure_ascii=False) + "\n")
            
        time.sleep(10)  # Avoid Gemini Free Tier rate limits

    print(f"Results saved to {out_path}")

if __name__ == "__main__":
    main()
