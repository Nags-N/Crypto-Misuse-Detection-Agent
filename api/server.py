import os
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import uuid
from typing import List

# Ensure parent directory is in path so we can import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.schemas import UploadResponse, AnalyzeRequest, AnalyzeResponse, FileAnalysisResult, ScanSummary
from agent.agent import CryptoMisuseAgent
from baselines.rule_based import predict_detailed
from preprocessing.parser import extract_features

app = FastAPI(title="CryptoGuard API")

# Setup CORS for local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for sessions: session_id -> dict of { filename: content_string }
sessions = {}
agent = CryptoMisuseAgent()

@app.post("/api/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())[:8]
    session_files = {}
    response_files = []

    for file in files:
        if file.filename.endswith(".java"):
            content = await file.read()
            text_content = content.decode("utf-8")
            session_files[file.filename] = text_content
            
            response_files.append({
                "name": file.filename,
                "size": len(content),
                "content": text_content
            })
    
    if not session_files:
        raise HTTPException(status_code=400, detail="No readable .java files provided.")

    sessions[session_id] = session_files

    return UploadResponse(
        session_id=session_id,
        files=response_files
    )

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_files(request: AnalyzeRequest):
    session_id = request.session_id
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found. Have you uploaded files?")

    session_files = sessions[session_id]
    filenames_to_analyze = request.files
    
    results = {}
    insecure_count = 0
    secure_count = 0

    for filename in filenames_to_analyze:
        if filename not in session_files:
            continue
            
        code = session_files[filename]
        file_result = FileAnalysisResult()
        is_insecure = False

        if request.mode in ["rule_based", "both"]:
            try:
                rb_report = predict_detailed(code)
                file_result.rule_based = {"label": rb_report.label, "triggered_rules": rb_report.triggered_rules}
                if rb_report.label == "insecure":
                    is_insecure = True
            except Exception as e:
                print(f"Rule-based error on {filename}: {e}")

        if request.mode in ["agent", "both"]:
            try:
                agent_report = agent.analyze(code)
                file_result.agent = agent_report.to_dict()
                if agent_report.label == "insecure":
                    is_insecure = True
            except Exception as e:
                print(f"Agent error on {filename}: {e}")
                # Fallback if agent crashes, e.g. rate limit
                file_result.agent = {"label": "error", "reasoning_trace": f"Error: {e}"}

        try:
            feats = extract_features(code)
            file_result.features = {
                "api_calls": feats.api_calls,
                "crypto_keywords": feats.crypto_keywords,
                "hardcoded_secrets": feats.hardcoded_secrets,
                "structural_tokens": feats.structural_tokens
            }
        except Exception as e:
            print(f"Feature extraction error on {filename}: {e}")

        results[filename] = file_result
        if is_insecure:
            insecure_count += 1
        else:
            secure_count += 1
            
    summary = ScanSummary(
        total_files=len(results),
        insecure_count=insecure_count,
        secure_count=secure_count
    )

    return AnalyzeResponse(
        session_id=session_id,
        status="complete",
        results=results,
        summary=summary
    )
