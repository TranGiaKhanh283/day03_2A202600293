import os
import time
import google.generativeai as genai
from typing import Dict, Any, List, Optional, Generator
from src.core.llm_provider import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-1.5-flash", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stop: Optional[List[str]] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        # In Gemini, system instruction is passed during model initialization or as a prefix
        # For simplicity in this lab, we'll prepend it if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

        cfg_kwargs: Dict[str, Any] = {}
        if stop:
            cfg_kwargs["stop_sequences"] = stop
        if temperature is not None:
            cfg_kwargs["temperature"] = temperature
        gen_cfg = genai.types.GenerationConfig(**cfg_kwargs) if cfg_kwargs else None

        response = self.model.generate_content(full_prompt, generation_config=gen_cfg)

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
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

        response = self.model.generate_content(full_prompt, stream=True)
        for chunk in response:
            yield chunk.text
