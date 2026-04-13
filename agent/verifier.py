import json
import logging
import os
from agent.llm_client import LLMClient
from agent.executor import FindingResult

logger = logging.getLogger(__name__)

class Verifier:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self._load_prompts()

    def _load_prompts(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            with open(os.path.join(root, "prompts", "system_prompt.txt"), "r") as f:
                self.system_prompt = f.read()
            with open(os.path.join(root, "prompts", "verification_prompt.txt"), "r") as f:
                self.verification_prompt_template = f.read()
        except FileNotFoundError as e:
            logger.error(f"Missing prompt file: {e}")
            self.system_prompt = "You are a secure code reviewer. Output verdict as secure or insecure in JSON."
            self.verification_prompt_template = "Code:\n{code_snippet}\n"

    def verify(self, code: str, initial_finding: FindingResult) -> FindingResult:
        prompt = self.verification_prompt_template.format(
            code_snippet=code,
            previous_verdict=initial_finding.verdict,
            previous_confidence=initial_finding.confidence,
            previous_explanation=initial_finding.explanation,
            previous_line_hint=initial_finding.line_hint or "None"
        )
        
        raw_response = self.llm.generate(prompt=prompt, system_prompt=self.system_prompt)
        return self._parse_response(raw_response)

    def _parse_response(self, text: str) -> FindingResult:
        try:
            if "```json" in text:
                json_text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                json_text = text.split("```")[1].strip()
            else:
                json_text = text.strip()
                
            if json_text.rfind("}") != -1:
                json_text = json_text[:json_text.rfind("}")+1]
                
            data = json.loads(json_text)
            verdict = data.get("verdict", "unknown").lower()
            if verdict not in ["secure", "insecure"]:
                verdict = "unknown"
                
            return FindingResult(
                verdict=verdict,
                confidence=data.get("confidence", "low").lower(),
                explanation=data.get("explanation", "Could not parse explanation."),
                line_hint=str(data.get("line_hint")) if data.get("line_hint") else None,
                raw_response=text
            )
        except Exception as e:
            logger.error(f"Failed to parse LLM response in Verifier: {e}")
            return FindingResult(
                verdict="unknown",
                confidence="low",
                explanation=f"Parsing error: {e}",
                line_hint=None,
                raw_response=text
            )
