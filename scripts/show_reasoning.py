import os
import sys
import json
import argparse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description="View Agent Reasoning Traces")
    parser.add_argument("--file", type=str, default="data/processed/agent_results.jsonl")
    parser.add_argument("--filter", type=str, choices=["secure", "insecure", "all"], default="all")
    args = parser.parse_args()

    results_path = os.path.join(PROJECT_ROOT, args.file)

    if not os.path.exists(results_path):
        print(f"File not found: {results_path}")
        sys.exit(1)

    print(f"Reading {args.file}...\n")

    with open(results_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
                
            data = json.loads(line)
            report = data.get("agent_report", {})
            meta = data.get("metadata", {})
            label = report.get("label", "UNKNOWN")
            
            if args.filter != "all" and label.lower() != args.filter:
                continue

            print("=" * 64)
            print(f"CASE: {meta.get('name', f'Sample {i+1}')}")
            print("-" * 64)
            print(f"AGENT REASONING:\n{report.get('reasoning_trace', 'No trace')}\n")
            
            findings = report.get("findings", [])
            finding = findings[-1] if findings else {}
            
            v = finding.get("verdict", "UNKNOWN").upper()
            c = finding.get("confidence", "UNKNOWN").upper()
            e = finding.get("explanation", "")
            
            print(f"VERDICT: {v}  |  Confidence: {c}")
            print(f"EXPLANATION: {e}")
            print("=" * 64 + "\n")

if __name__ == "__main__":
    main()
