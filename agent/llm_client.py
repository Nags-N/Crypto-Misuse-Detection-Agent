import os
import time
import logging
from typing import Optional
from dotenv import load_dotenv

# Load explicitly from root .env if it exists
root_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=root_env)

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Provider-agnostic LLM client wrapper.
    Currently supports Google Gemini via google-genai.
    """
    def __init__(
        self, 
        provider: str = "gemini", 
        model: str = "gemini-2.0-flash", 
        temperature: float = 0.1, 
        max_tokens: int = 2048, 
        max_retries: int = 3
    ):
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        
        if self.provider == "gemini":
            if not HAS_GENAI:
                raise ImportError("google-genai is not installed. Please install it with: pip install google-genai")
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key or api_key == "your_key_here":
                raise ValueError("GEMINI_API_KEY environment variable is not set correctly.")
            self.client = genai.Client(api_key=api_key)
        else:
            raise NotImplementedError(f"Provider {self.provider} not supported yet.")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generates text using the configured LLM with retry logic.
        """
        for attempt in range(self.max_retries):
            try:
                if self.provider == "gemini":
                    return self._generate_gemini(prompt, system_prompt)
            except Exception as e:
                logger.warning(f"LLM Generation failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise
                if "429" in str(e):
                    import time
                    time.sleep(30 + (20 * attempt))
                else:
                    import time
                    time.sleep(2 ** attempt)
        return ""

    def _generate_gemini(self, prompt: str, system_prompt: Optional[str]) -> str:
        config_dict = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }
        if system_prompt:
            config_dict["system_instruction"] = system_prompt
            
        config = types.GenerateContentConfig(**config_dict)
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )
        return response.text
