"""
LLM Abstraction Layer - Provider-agnostic interface for AI models.
Supports Claude, Gemini, and open-source models via Ollama.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import os
import json


@dataclass
class LLMResponse:
    """Standard response from any LLM provider."""
    content: str
    model: str
    usage: dict[str, int] | None = None
    raw_response: Any = None


@dataclass
class Message:
    """Chat message format."""
    role: str  # "user", "assistant", "system"
    content: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def complete(self, prompt: str, system: str | None = None) -> LLMResponse:
        """Single completion request."""
        pass

    @abstractmethod
    def chat(self, messages: list[Message], system: str | None = None) -> LLMResponse:
        """Multi-turn conversation."""
        pass

    @abstractmethod
    def analyze(self, content: str, schema: dict) -> dict:
        """Analyze content and return structured JSON matching schema."""
        pass


class ClaudeAdapter(LLMProvider):
    """Anthropic Claude adapter."""

    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package required: pip install anthropic")
        return self._client

    def complete(self, prompt: str, system: str | None = None) -> LLMResponse:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}]
        )
        return LLMResponse(
            content=response.content[0].text,
            model=self.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            raw_response=response
        )

    def chat(self, messages: list[Message], system: str | None = None) -> LLMResponse:
        formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system or "You are a helpful assistant.",
            messages=formatted_messages
        )
        return LLMResponse(
            content=response.content[0].text,
            model=self.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            raw_response=response
        )

    def analyze(self, content: str, schema: dict) -> dict:
        prompt = f"""Analyze the following content and return a JSON object matching this schema:

Schema:
```json
{json.dumps(schema, indent=2)}
```

Content to analyze:
```
{content}
```

Return ONLY valid JSON, no explanations."""

        response = self.complete(prompt, system="You are a precise analyzer. Return only valid JSON.")

        # Extract JSON from response
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        return json.loads(text)


class GeminiAdapter(LLMProvider):
    """Google Gemini adapter."""

    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-pro"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError("google-generativeai package required: pip install google-generativeai")
        return self._client

    def complete(self, prompt: str, system: str | None = None) -> LLMResponse:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = self.client.generate_content(full_prompt)
        return LLMResponse(
            content=response.text,
            model=self.model,
            raw_response=response
        )

    def chat(self, messages: list[Message], system: str | None = None) -> LLMResponse:
        chat = self.client.start_chat(history=[])

        for msg in messages[:-1]:
            if msg.role == "user":
                chat.send_message(msg.content)

        last_msg = messages[-1]
        response = chat.send_message(last_msg.content)

        return LLMResponse(
            content=response.text,
            model=self.model,
            raw_response=response
        )

    def analyze(self, content: str, schema: dict) -> dict:
        prompt = f"""Analyze the following content and return a JSON object matching this schema:

Schema:
```json
{json.dumps(schema, indent=2)}
```

Content to analyze:
```
{content}
```

Return ONLY valid JSON, no explanations."""

        response = self.complete(prompt)

        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        return json.loads(text)


class OllamaAdapter(LLMProvider):
    """Ollama adapter for local open-source models."""

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def _request(self, endpoint: str, data: dict) -> dict:
        import urllib.request
        import urllib.error

        url = f"{self.base_url}{endpoint}"
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())

    def complete(self, prompt: str, system: str | None = None) -> LLMResponse:
        data = {
            "model": self.model,
            "prompt": prompt,
            "system": system or "",
            "stream": False
        }
        response = self._request("/api/generate", data)
        return LLMResponse(
            content=response["response"],
            model=self.model,
            raw_response=response
        )

    def chat(self, messages: list[Message], system: str | None = None) -> LLMResponse:
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        formatted_messages.extend([{"role": m.role, "content": m.content} for m in messages])

        data = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": False
        }
        response = self._request("/api/chat", data)
        return LLMResponse(
            content=response["message"]["content"],
            model=self.model,
            raw_response=response
        )

    def analyze(self, content: str, schema: dict) -> dict:
        prompt = f"""Analyze the following content and return a JSON object matching this schema:

Schema:
```json
{json.dumps(schema, indent=2)}
```

Content to analyze:
```
{content}
```

Return ONLY valid JSON, no explanations."""

        response = self.complete(prompt)

        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        return json.loads(text)


def get_provider(provider_name: str = "claude", **kwargs) -> LLMProvider:
    """Factory function to get the appropriate LLM provider."""
    providers = {
        "claude": ClaudeAdapter,
        "gemini": GeminiAdapter,
        "ollama": OllamaAdapter,
    }

    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(providers.keys())}")

    return providers[provider_name](**kwargs)
