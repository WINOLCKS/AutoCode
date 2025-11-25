import requests
from typing import List, Dict


class Searcher:
    def search(self, query: str) -> List[Dict[str, str]]:
        """
        执行 Web 搜索，返回结果列表。
        :param query: 搜索查询字符串
        :return: 结果列表，每个结果包含 'title' 和 'url'
        :raises ValueError: 如果查询为空
        """
        if not query.strip():
            raise ValueError("搜索查询不能为空")

        # 使用 DuckDuckGo 免费 API 示例（替换为实际 API 如果需要）
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"搜索失败: {response.status_code}")

        data = response.json()
        results = []
        for related in data.get('RelatedTopics', []):
            if 'Text' in related and 'FirstURL' in related:
                results.append({
                    'title': related['Text'],
                    'url': related['FirstURL']
                })
        return results