import requests
import json

# 云端配置
endpoint = "https://api.newcoin.top/v1/chat/completions"
api_key = "sk-Es7vcBoepmOZxuvjhZg6aDZk3AujnjErmSq6Hi7xI0poOkRC"
model = "doubao-seed-1-6-251015"

# 测试payload
payload = {
    "model": model,
    "messages": [{"role": "user", "content": "我发送32Ktokens长度的文本你可以成功读取么"}],
    "temperature": 0.2
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    response = requests.post(endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        print("API可用！响应内容：")
        print(response.json()['choices'][0]['message']['content'])
    else:
        print(f"API不可用，状态码：{response.status_code}")
        print(f"错误详情：{response.text}")
except Exception as e:
    print(f"连接错误：{str(e)}")
    print("建议检查API服务器、Key或网络。")