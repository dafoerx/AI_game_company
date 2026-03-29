import json
import re
import time

import requests


# 已知的 API 网关错误模式
# 当上游模型返回 500 时，网关可能将错误信息包装在 SSE chunk 的 content 中返回
_ERROR_PATTERNS = [
    re.compile(r"^codex:\s*status=\d+", re.IGNORECASE),
    re.compile(r"^error:\s*status=\d+", re.IGNORECASE),
    re.compile(r"^internal server error$", re.IGNORECASE),
    re.compile(r"^5\d{2}\s+(internal server error|bad gateway|service unavailable|gateway timeout)", re.IGNORECASE),
]


class LLMResponseError(RuntimeError):
    """LLM 返回了非正常内容（如网关 500 错误被包装为正常响应）。"""
    pass


class LLMClient(object):
    def __init__(self, base_url, api_key, model, max_retries=3, retry_delay=5):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def complete(self, system_prompt, user_prompt):
        """
        调用 LLM 生成内容，带自动重试机制。

        当检测到以下情况时自动重试（最多 max_retries 次）：
        1. HTTP 层面的 5xx 错误
        2. 网关将 500 错误包装成 SSE content 返回
        3. 网络超时
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                result = self._do_request(system_prompt, user_prompt)

                # ── 关键校验：检查返回内容是否是伪装成正常响应的错误信息 ──
                self._check_for_error_content(result)

                return result

            except (LLMResponseError, requests.exceptions.HTTPError) as exc:
                last_error = exc
                if attempt < self.max_retries:
                    wait = self.retry_delay * attempt  # 递增等待：5s, 10s, 15s
                    print(f"[LLM] ⚠️ 第 {attempt} 次调用失败: {exc}，{wait}s 后重试...")
                    time.sleep(wait)
                else:
                    print(f"[LLM] ❌ 已重试 {self.max_retries} 次仍然失败: {exc}")

            except requests.exceptions.Timeout as exc:
                last_error = exc
                if attempt < self.max_retries:
                    wait = self.retry_delay * attempt
                    print(f"[LLM] ⚠️ 第 {attempt} 次调用超时，{wait}s 后重试...")
                    time.sleep(wait)
                else:
                    print(f"[LLM] ❌ 已重试 {self.max_retries} 次仍然超时")

            except requests.exceptions.ConnectionError as exc:
                last_error = exc
                if attempt < self.max_retries:
                    wait = self.retry_delay * attempt
                    print(f"[LLM] ⚠️ 第 {attempt} 次连接失败，{wait}s 后重试...")
                    time.sleep(wait)
                else:
                    print(f"[LLM] ❌ 已重试 {self.max_retries} 次仍然连接失败")

        raise last_error

    def _do_request(self, system_prompt, user_prompt):
        """执行单次 LLM API 请求。"""
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

    @staticmethod
    def _check_for_error_content(text):
        """
        检测 LLM 返回内容是否为伪装成正常响应的错误信息。

        某些 API 网关会将上游 500 错误包装成 HTTP 200 + SSE 格式返回，
        其中 delta.content 实际内容是错误信息，如：
          "codex: status=500 Internal Server Error"

        这种情况下 raise_for_status() 不会报错，需要在内容层面检测。
        """
        if not text:
            raise LLMResponseError("LLM 返回了空内容")

        # 短文本更可能是错误信息（正常代码至少几十行）
        stripped = text.strip()
        if len(stripped) < 100:
            for pattern in _ERROR_PATTERNS:
                if pattern.search(stripped):
                    raise LLMResponseError(f"LLM 网关返回了伪装成正常响应的错误: {stripped}")
