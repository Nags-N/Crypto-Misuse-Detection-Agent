import logging
import yaml
import os
from dataclasses import dataclass, asdict
from typing import List

from agent.llm_client import LLMClient
from agent.planner import Planner
from agent.executor import Executor, FindingResult
from agent.verifier import Verifier

logger = logging.getLogger(__name__)

@dataclass
class AgentReport:
    label: str
    confidence: str
    findings: List[dict]
    reasoning_trace: str
    
    def to_dict(self):
        return asdict(self)

class CryptoMisuseAgent:
    def __init__(self, config_path: str = "configs/phase2.yaml"):
        # Load config logic that works from any working directory
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        safe_config_path = os.path.join(root, config_path)
        
        with open(safe_config_path, "r") as f:
            self.config = yaml.safe_load(f)
            
        llm_cfg = self.config.get("llm", {})
        agent_cfg = self.config.get("agent", {})
        
        self.llm_client = LLMClient(
            provider=llm_cfg.get("provider", "gemini"),
            model=llm_cfg.get("model", "gemini-2.0-flash"),
            temperature=llm_cfg.get("temperature", 0.1),
            max_tokens=llm_cfg.get("max_tokens", 2048),
            max_retries=llm_cfg.get("max_retries", 3)
        )
        
        self.planner = Planner(max_features=agent_cfg.get("max_features_in_prompt", 10))
        self.executor = Executor(self.llm_client)
        self.use_verifier = agent_cfg.get("use_verifier", True)
        if self.use_verifier:
            self.verifier = Verifier(self.llm_client)

    def analyze(self, code: str) -> AgentReport:
        logger.debug("Planning analysis...")
        context = self.planner.plan_analysis(code)
        
        logger.debug("Executing initial analysis...")
        initial_finding = self.executor.execute_analysis(code, context)
        final_finding = initial_finding
        
        if self.use_verifier:
            logger.debug("Running verifier pass...")
            verification_finding = self.verifier.verify(code, initial_finding)
            final_finding = verification_finding
            
            trace = f"--- INITIAL ANALYSIS ---\n{initial_finding.raw_response}\n\n--- VERIFICATION PASS ---\n{verification_finding.raw_response}"
        else:
            trace = f"--- INITIAL ANALYSIS ---\n{initial_finding.raw_response}"

        # Treat 'unknown' predictions conservatively as insecure to be safe
        predict_label = final_finding.verdict
        if predict_label not in ["secure", "insecure"]:
            predict_label = "insecure"

        return AgentReport(
            label=predict_label,
            confidence=final_finding.confidence,
            findings=[asdict(final_finding)],
            reasoning_trace=trace
        )
