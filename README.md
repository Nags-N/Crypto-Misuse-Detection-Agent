# Crypto-Misuse-Detection-Agent

**Reasoning-Based Detection of Cryptographic Misuse Using Agentic AI**

A research project that detects cryptographic API misuse in Java source code using rule-based heuristics and machine-learning baselines. This repository covers the infrastructure, data pipeline, and baseline evaluation — the foundation for later agentic AI reasoning.

> ⚠️ **Scope**: This codebase implements data loading, preprocessing, baselines, and evaluation only. No LLMs or agentic reasoning are included yet.

---

## 📁 Project Structure

```
Crypto-Misuse-Detection-Agent/
├── data/
│   ├── raw/                  # Place benchmark datasets here
│   └── processed/            # Generated JSONL files
├── datasets/
│   ├── cryptoapi_bench.py    # CryptoAPI-Bench loader
│   └── owasp_benchmark.py   # OWASP Benchmark loader
├── preprocessing/
│   ├── parser.py             # Feature extraction (API calls, keywords)
│   └── normalizer.py         # Code normalization (whitespace, comments)
├── baselines/
│   ├── rule_based.py         # Rule-based misuse detector
│   └── simple_classifier.py  # TF-IDF + Logistic Regression
├── evaluation/
│   ├── metrics.py            # Accuracy, Precision, Recall, F1
│   └── evaluate.py           # Run evaluation and print results
├── scripts/
│   ├── setup_env.sh          # Environment setup script
│   ├── prepare_data.py       # Dataset preparation pipeline
│   └── run_baseline.py       # Run baselines and evaluate
├── configs/
│   └── default.yaml          # Default configuration
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 Setup

### Prerequisites
- Python 3.10+
- Git

### Install Dependencies

**Linux / macOS:**
```bash
bash scripts/setup_env.sh
```

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📦 Data Preparation

### 1. Download Datasets

Clone the benchmark datasets into `data/raw/`:

```bash
cd data/raw
git clone https://github.com/CryptoGuardOSS/cryptoapi-bench.git cryptoapi_bench
git clone https://github.com/OWASP-Benchmark/BenchmarkJava.git owasp_benchmark
```

### 2. Process Data

```bash
python scripts/prepare_data.py
```

This merges both datasets into `data/processed/dataset.jsonl`.

---

## ▶️ Running Baselines

```bash
python scripts/run_baseline.py
```

This runs both baselines (rule-based + TF-IDF classifier) and prints a metrics table:

```
┌─────────────────────────┬──────────┬───────────┬────────┬────────┐
│ Model                   │ Accuracy │ Precision │ Recall │ F1     │
├─────────────────────────┼──────────┼───────────┼────────┼────────┤
│ Rule-Based              │ 0.XX     │ 0.XX      │ 0.XX   │ 0.XX   │
│ TF-IDF + LogReg         │ 0.XX     │ 0.XX      │ 0.XX   │ 0.XX   │
└─────────────────────────┴──────────┴───────────┴────────┴────────┘
```

---

## ⚙️ Configuration

Edit `configs/default.yaml` to change:
- Dataset paths
- Train/test split ratio
- Random seed
- Preprocessing options

---

## 📄 License

This project is for research purposes.
