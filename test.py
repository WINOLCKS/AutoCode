import ollama

response = ollama.generate(model='qwen3:8b', prompt='测试本地模型：输出 "Hello, Qwen3!"')
print(response['response'])