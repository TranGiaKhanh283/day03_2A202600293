import os
import time
from google import genai
from typing import Dict, Any, List, Optional, Generator
from src.core.llm_provider import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-2.5-flash-lite", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        if not self.api_key:
            self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stop: Optional[List[str]] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        cfg_kwargs = {}
        if stop:
            cfg_kwargs["stop_sequences"] = stop
        if temperature is not None:
            cfg_kwargs["temperature"] = temperature
        if system_prompt:
            cfg_kwargs["system_instruction"] = system_prompt
            
        gen_cfg = genai.types.GenerateContentConfig(**cfg_kwargs) if cfg_kwargs else None

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=gen_cfg
        )

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        try:
            content = response.text
        except ValueError:
            content = ""
            
        um = response.usage_metadata
        if um is None:
            usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        else:
            usage = {
                "prompt_tokens": getattr(um, "prompt_token_count", 0) or 0,
                "completion_tokens": getattr(um, "candidates_token_count", 0) or 0,
                "total_tokens": getattr(um, "total_token_count", 0) or 0,
            }

        return {
            "content": content,
            "usage": usage,
            "latency_ms": latency_ms,
            "provider": "google"
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        cfg_kwargs = {}
        if system_prompt:
            cfg_kwargs["system_instruction"] = system_prompt
            
        gen_cfg = genai.types.GenerateContentConfig(**cfg_kwargs) if cfg_kwargs else None

        response_stream = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=prompt,
            config=gen_cfg
        )
        
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
