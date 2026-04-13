# Crypto-Misuse-Detection-Agent

**Reasoning-Based Detection of Cryptographic Misuse Using Agentic AI**

A research project that detects cryptographic API misuse in Java source code. This project moves beyond traditional static analysis by combining rule-based heuristics with **Agentic AI**—a system capable of step-by-step reasoning about code context, data flow, and security implications.

---

## 📁 Project Structure

```
Crypto-Misuse-Detection-Agent/
├── agent/                  # Core Agentic System (Planner, Executor, Verifier)
├── prompts/                # Versioned LLM prompt templates
├── data/
│   ├── raw/                # Benchmark repository clones
│   ├── processed/          # Merged datasets and agent results
│   └── hard_cases/         # Curated challenging test cases for reasoning
├── datasets/               # Data loaders (CryptoAPI-Bench & OWASP)
├── preprocessing/          # Static feature extraction & normalization
├── baselines/              # Traditional detectors (Rule-based & ML)
├── evaluation/             # Metrics, Explainability, and Calibration scoring
├── scripts/
│   ├── prepare_data.py     # Main data pipeline
│   ├── run_baseline.py     # Execute traditional models
│   └── run_agent.py        # Execute Agentic AI analysis
├── configs/
│   ├── default.yaml        # Phase 1 Config
│   └── phase2.yaml         # LLM & Agent Config
├── .env                    # Private API Keys (User-created)
├── requirements.txt
└── README.md
```

---

## 🚀 Setup

### Prerequisites
- Python 3.10+
- Git
- **Google Gemini API Key** (Get it at [Google AI Studio](https://aistudio.google.com/))

### Install Dependencies
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### LLM Setup (API Key)
1. Copy `.env.example` to a new file named `.env`.
2. Insert your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_key_here
   ```

---

## 📦 Data Preparation

### 1. Download Datasets
Clone the benchmarks into `data/raw/`:
```bash
cd data/raw
git clone https://github.com/CryptoGuardOSS/cryptoapi-bench.git cryptoapi_bench
git clone https://github.com/OWASP-Benchmark/BenchmarkJava.git owasp_benchmark
```

### 2. Process Data
```bash
python scripts/prepare_data.py
```

---

## ▶️ Running Analysis

### 1. Run Traditional Baselines
Fast, rule-based scanning and simple ML classification:
```bash
python scripts/run_baseline.py
```

### 2. Run Agentic AI Detector
The reasoning-based detector (Chain-of-Thought). Use `--test-run` for a quick scan of the hard-case dataset:
```bash
python scripts/run_agent.py --dataset data/hard_cases/hard_cases.jsonl --test-run
```

### 3. Compare Results
View the comparison between Baselines and the Agentic approach:
```bash
python scripts/compare_baselines.py
```

---

## 🧪 Phase 2: Agentic AI Features

Unlike simple scanners, the Agentic AI in this project provides:
- **Step-by-Step Reasoning**: Explains exactly *why* a snippet is insecure.
- **Context Awareness**: Distinguishes between suspicious variable names and actual insecure logic.
- **Critic Pass**: Implements a self-reflection step where the AI reviews its own findings to reduce false positives.
- **Explainability**: Outputs structured reports with justifications and line hints.

---

## 📄 License

This project is for research purposes.
