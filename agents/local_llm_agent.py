import ollama
import logging

logger = logging.getLogger(__name__)

class LocalLLMAgent:
    def __init__(self, model='qwen3:4b', temperature=0.2):
        self.model = model
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        """使用 Ollama 生成响应"""
        try:
            response = ollama.generate(model='qwen3:4b', prompt=prompt, options={'temperature': 0.2, 'num_ctx': 16384})
            return response['response'].strip()
        except Exception as e:
            logger.error(f"Ollama 生成失败: {str(e)}")
            return ""  # 返回空字符串，避免中断