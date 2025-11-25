# SRS文档 - 待办事项管理工具小程序


## 1. 原始需求摘录  
用户需求：**"请为我编写一个计算机小程序"**  
因需求宽泛，结合实用场景，将程序定位为**待办事项管理工具**，核心目标是帮助用户高效管理待办任务，支持添加、查看、更新（标记完成）、删除等基础操作。


## 2. 功能点清单  
| 功能ID | 功能描述 | 输入 | 输出 |
|--------|----------|------|------|
| F01    | 添加待办任务 | 任务内容（字符串） | 新增任务详情（ID、内容、状态） |
| F02    | 查看所有任务 | 无 | 所有任务列表（含ID、内容、完成状态） |
| F03    | 标记任务完成 | 任务ID（整数） | 操作结果（成功/失败） |
| F04    | 删除指定任务 | 任务ID（整数） | 操作结果（成功/失败） |
| F05    | 清空所有任务 | 无 | 无（任务列表清空） |


## 3. 接口签名设计（Python类）  
```python
class TodoManager:
    """待办事项管理类"""
    
    def __init__(self) -> None:
        """初始化空任务列表"""
        self.tasks: list[dict] = []
        self._next_id: int = 1  # 自动递增的任务ID
    
    def add_task(self, content: str) -> dict:
        """添加新任务  
        Args: content - 任务内容  
        Returns: 任务字典（id: int, content: str, done: bool）  
        """
        task = {"id": self._next_id, "content": content, "done": False}
        self.tasks.append(task)
        self._next_id += 1
        return task
    
    def get_all_tasks(self) -> list[dict]:
        """获取所有任务列表  
        Returns: 任务字典列表  
        """
        return self.tasks.copy()  # 返回副本避免外部修改
    
    def mark_task_done(self, task_id: int) -> bool:
        """标记任务为完成  
        Args: task_id - 任务ID  
        Returns: True（成功）/False（无此ID）  
        """
        for task in self.tasks:
            if task["id"] == task_id:
                task["done"] = True
                return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """删除指定任务  
        Args: task_id - 任务ID  
        Returns: True（成功）/False（无此ID）  
        """
        initial_length = len(self.tasks)
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        return len(self.tasks) < initial_length
    
    def clear_all_tasks(self) -> None:
        """清空所有任务"""
        self.tasks.clear()
        self._next_id = 1  # 重置ID计数器
```


## 4. pytest验收用例  
```python
import pytest
from todo_manager import TodoManager  # 假设类定义在todo_manager.py中

def test_initialization():
    """测试初始化时任务列表为空"""
    manager = TodoManager()
    assert manager.get_all_tasks() == []

def test_add_task():
    """测试添加任务功能"""
    manager = TodoManager()
    task = manager.add_task("Buy groceries")
    # 检查返回的任务信息
    assert task["content"] == "Buy groceries"
    assert task["done"] is False
    assert isinstance(task["id"], int) == True
    # 检查任务列表是否包含新增任务
    all_tasks = manager.get_all_tasks()
    assert len(all_tasks) == 1
    assert all_tasks[0]["id"] == task["id"]

def test_get_all_tasks():
    """测试查看所有任务功能"""
    manager = TodoManager()
    task1 = manager.add_task("Read book")
    task2 = manager.add_task("Write code")
    all_tasks = manager.get_all_tasks()
    assert len(all_tasks) == 2
    assert task1 in all_tasks
    assert task2 in all_tasks

def test_mark_task_done():
    """测试标记任务完成功能"""
    manager = TodoManager()
    task = manager.add_task("Exercise")
    task_id = task["id"]
    # 标记存在的任务
    assert manager.mark_task_done(task_id) == True
    updated_task = manager.get_all_tasks()[0]
    assert updated_task["done"] is True
    # 标记不存在的任务
    assert manager.mark_task_done(999) == False

def test_delete_task():
    """测试删除任务功能"""
    manager = TodoManager()
    task = manager.add_task("Clean room")
    task_id = task["id"]
    # 删除存在的任务
    assert manager.delete_task(task_id) == True
    assert len(manager.get_all_tasks()) == 0
    # 删除不存在的任务
    assert manager.delete_task(999) == False

def test_clear_all_tasks():
    """测试清空所有任务功能"""
    manager = TodoManager()
    manager.add_task("Task1")
    manager.add_task("Task2")
    manager.clear_all_tasks()
    assert manager.get_all_tasks() == []
    # 检查ID计数器重置
    new_task = manager.add_task("New task")
    assert new_task["id"] == 1
```


## 5. 运行说明  
1. 将接口类代码保存为`todo_manager.py`  
2. 将测试用例保存为`test_todo_manager.py`  
3. 安装pytest：`pip install pytest`  
4. 执行测试：`pytest test_todo_manager.py -v`  
5. 所有测试用例通过即表示功能符合需求  

此文档覆盖了待办工具的核心功能，接口设计简洁易用，测试用例覆盖所有场景，可直接用于开发和验证。
```