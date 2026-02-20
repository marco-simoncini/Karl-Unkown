from __future__ import annotations

from typing import List, Dict

import httpx


class OllamaClient:
    def __init__(
        self, base_url: str, model: str, timeout_seconds: float, api_key: str | None = None
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.api_key = api_key

    async def chat(self, system_prompt: str, user_prompt: str) -> str:
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # noqa: BLE001
            return (
                "LLM endpoint not reachable. Returning deterministic fallback. "
                f"Reason: {exc}"
            )

        choices = data.get("choices", [])
        if not choices:
            return "LLM returned no choices. Please check runtime logs."

        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return content

        return "LLM returned an unexpected response format."
