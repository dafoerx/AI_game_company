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
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
