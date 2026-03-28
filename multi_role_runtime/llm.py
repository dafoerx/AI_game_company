import json

import requests


class LLMClient(object):
    def __init__(self, base_url, api_key, model):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def complete(self, system_prompt, user_prompt):
        url = self.base_url + "/chat/completions"
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=300)
        resp.raise_for_status()

        try:
            data = resp.json()
            return (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
        except ValueError:
            # 兼容部分网关返回 SSE 文本（data: ...）而非标准 JSON
            # 强制按 UTF-8 解码，避免中文被按 Latin-1 解释后出现乱码。
            raw_text = resp.content.decode("utf-8", errors="replace")
            parts = []
            for line in raw_text.splitlines():
                line = line.strip()
                if not line.startswith("data:"):
                    continue
                chunk = line[5:].strip()
                if not chunk or chunk == "[DONE]":
                    continue
                try:
                    item = json.loads(chunk)
                except Exception:
                    continue
                delta = (item.get("choices", [{}])[0].get("delta", {}) or {})
                message = (item.get("choices", [{}])[0].get("message", {}) or {})
                content = delta.get("content") or message.get("content")
                if content:
                    parts.append(content)

            text = "".join(parts).strip()
            if text:
                return text
            raise RuntimeError("LLM 返回了无法解析的响应格式")
