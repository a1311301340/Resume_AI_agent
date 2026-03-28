from __future__ import annotations

from typing import Any

import httpx


class BailianAppClient:
    def __init__(self, api_key: str, app_id: str, completion_url: str, timeout_sec: int = 60) -> None:
        self.api_key = api_key
        self.app_id = app_id
        self.completion_url = completion_url
        self.timeout_sec = timeout_sec

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.app_id and self.completion_url and "/apps/" in self.completion_url)

    def complete(self, prompt: str, history: list[dict[str, Any]] | None = None) -> str:
        if not self.enabled:
            raise RuntimeError("Bailian client is not configured.")

        final_prompt = self._build_prompt(prompt=prompt, history=history or [])
        payload = {
            "input": {
                "prompt": final_prompt,
            },
            "parameters": {},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=self.timeout_sec) as client:
            response = client.post(self.completion_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        return self._extract_text(data)

    def _build_prompt(self, prompt: str, history: list[dict[str, Any]]) -> str:
        if not history:
            return prompt

        # Keep recent context lightweight to reduce token cost and latency.
        recent = history[-6:]
        context_lines: list[str] = ["以下是最近对话上下文："]
        for item in recent:
            role = str(item.get("role", "user"))
            content = str(item.get("content", "")).strip()
            if not content:
                continue
            context_lines.append(f"{role}: {content}")
        context_lines.append("请基于以上上下文回答用户当前问题：")
        context_lines.append(prompt)
        return "\n".join(context_lines)

    def _extract_text(self, data: dict[str, Any]) -> str:
        output = data.get("output")
        if isinstance(output, dict):
            text = output.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()

            choices = output.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    message = first.get("message")
                    if isinstance(message, dict):
                        content = message.get("content")
                        if isinstance(content, str) and content.strip():
                            return content.strip()
                    text2 = first.get("text")
                    if isinstance(text2, str) and text2.strip():
                        return text2.strip()

        # Fallback for any unexpected payload shape.
        if isinstance(data.get("message"), str):
            return str(data["message"])
        return "模型返回为空，请稍后重试。"
