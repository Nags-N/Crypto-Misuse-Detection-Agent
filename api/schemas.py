from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class UploadResponse(BaseModel):
    session_id: str
    files: List[Dict[str, Any]]

class AnalyzeRequest(BaseModel):
    session_id: str
    files: List[str]  # List of filenames to analyze
    mode: str = "both"  # "agent", "rule_based", or "both"

class FileAnalysisResult(BaseModel):
    agent: Optional[Dict[str, Any]] = None
    rule_based: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any]] = None

class ScanSummary(BaseModel):
    total_files: int
    insecure_count: int
    secure_count: int

class AnalyzeResponse(BaseModel):
    session_id: str
    status: str
    results: Dict[str, FileAnalysisResult]
    summary: ScanSummary
