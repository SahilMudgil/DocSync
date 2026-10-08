"""
LLM Factory for DocSync.
Provides chat completion interfaces for:
- Fake (for 100% offline deterministic testing without API keys)
- Google Gemini API (cloud-hosted)
- Ollama (running locally or on an AWS EC2 instance)
"""

import os
import json
import requests
from typing import Dict, Any


class ChatModelInterface:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError


class FakeChatModel(ChatModelInterface):
    """Deterministic model for offline testing and smoke tests."""

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        # Check if user prompt is checking timeout=60 vs 30
        if "timeout=60" in user_prompt or "60" in user_prompt:
            return json.dumps({
                "decision": "DRIFT",
                "confidence": 0.95,
                "reason": "Parameter timeout changed from 30 to 60 in code but documentation still states 30.",
                "evidence_ids": ["E2", "D1"],
            })
        elif "Query:" in user_prompt:
            return "Based on the repository, fetch_data() connects to the given URL and has a default timeout parameter. Cited: client.py:1-15."
        else:
            return json.dumps({
                "decision": "MATCH",
                "confidence": 0.90,
                "reason": "Code implementation matches the documented behavior.",
                "evidence_ids": ["E2", "D1"],
            })


class OllamaChatModel(ChatModelInterface):
    """Calls an Ollama instance (running locally or on an AWS EC2 server)."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "deepseek-coder:6.7b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.0},
        }
        try:
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("message", {}).get("content", "")
            return f'{{"decision": "MODEL_ERROR", "confidence": 0.0, "reason": "Ollama error {resp.status_code}", "evidence_ids": []}}'
        except Exception as e:
            return f'{{"decision": "MODEL_ERROR", "confidence": 0.0, "reason": "Connection to Ollama failed: {str(e)}", "evidence_ids": []}}'


class GeminiChatModel(ChatModelInterface):
    """Calls Google Gemini REST API using GOOGLE_API_KEY."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt = f"{system_prompt}\n\n{user_prompt}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.0},
        }
        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return f'{{"decision": "MODEL_ERROR", "confidence": 0.0, "reason": "Gemini error {resp.status_code}", "evidence_ids": []}}'
        except Exception as e:
            return f'{{"decision": "MODEL_ERROR", "confidence": 0.0, "reason": "Gemini API call failed: {str(e)}", "evidence_ids": []}}'


def get_chat_model(provider: str = "fake", model: str = "gemini-1.5-flash", **kwargs) -> ChatModelInterface:
    """Return appropriate ChatModelInterface based on provider."""
    provider = provider.lower()
    if provider == "gemini":
        key = os.getenv("GOOGLE_API_KEY", "")
        if key:
            return GeminiChatModel(api_key=key, model=model)
        # Fallback to fake if key missing
        return FakeChatModel()
    elif provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaChatModel(base_url=base_url, model=model)
    return FakeChatModel()
