import os

class FileReader:
    def read(self, file_path: str) -> str:
        """
        读取指定文件的内容。
        :param file_path: 文件路径
        :return: 文件内容字符串
        :raises FileNotFoundError: 如果文件不存在
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()