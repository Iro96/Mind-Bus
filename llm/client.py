import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

try:
    import openai
except ImportError:
    openai = None


class LLMClient:
    """Simple LLM client wrapper using OpenAI API (or mock fallback)."""

    def __init__(self, model: str = "gpt-4.1", temperature: float = 0.2):
        self.model = model
        self.temperature = temperature

        api_key = os.environ.get("OPENAI_API_KEY")
        if openai and api_key:
            openai.api_key = api_key
            self.enabled = True
        else:
            self.enabled = False
            if not openai:
                logger.warning("openai package not installed; LLM calls are mocked")
            else:
                logger.warning("OPENAI_API_KEY not set; LLM calls are mocked")

    def _mock_response(self, prompt: str) -> str:
        return "{\"issue_source\": \"generation error\", \"candidate_fix\": \"Use explicit tool calls and validate outputs.\", \"valid_fix\": true}"

    def chat_completion(self, messages: List[Dict[str, Any]], max_tokens: int = 512) -> Dict[str, Any]:
        if not self.enabled:
            raw = self._mock_response("\n".join([m['content'] for m in messages]))
            try:
                return json.loads(raw)
            except Exception:
                return {"content": raw}

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=max_tokens,
        )

        if response and response.choices:
            text = response.choices[0].message.get("content", "")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"content": text}

        return {"error": "empty_response"}

    def generate_text(self, prompt: str, max_tokens: int = 256) -> str:
        if not self.enabled:
            return "[mock response] please set OPENAI_API_KEY to enable real LLM output."

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=max_tokens,
        )
        if response and response.choices:
            return response.choices[0].message.get("content", "")
        return ""
