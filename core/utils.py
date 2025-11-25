import requests
import json
import yaml
import os

class LLMClient:
    def __init__(self, config):
        self.api_key = os.getenv('CLOUD_API_KEY', config['api_key'])  # 优先环境变量，提高安全性
        self.model = config['model']
        self.endpoint = f"{config['base_url']}{config['path']}"
        self.default_temperature = config.get('temperature_code', 0.2)

    def generate(self, prompt: str, temperature=None, max_tokens=4096) -> str:
        """生成响应，支持 OpenAI 兼容格式"""
        if temperature is None:
            temperature = self.default_temperature
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": "You are a helpful code generation assistant."},  # 系统提示，可自定义
                         {"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(self.endpoint, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"API 调用失败: {response.status_code} - {response.text}")