# 待办事项管理程序 SRS文档


## 1. 原始需求摘录  
用户需求：开发一个简单的待办事项管理小程序，支持**添加待办、删除待办、查看所有待办、标记待办为已完成**的核心功能，要求操作直观、状态清晰。


## 2. 功能点清单  
| 功能模块               | 描述                                                                 |
|------------------------|----------------------------------------------------------------------|
| 添加待办事项           | 输入待办内容，生成唯一ID并存储，禁止空内容添加                       |
| 删除待办事项           | 根据ID删除指定待办，支持判断ID是否存在                               |
| 查看所有待办事项       | 返回所有待办列表，包含ID、内容、完成状态（未完成/已完成）             |
| 标记待办为已完成       | 根据ID更新待办状态为“已完成”，支持判断ID是否存在                     |


## 3. 接口签名设计  
采用Python类`TodoManager`封装核心逻辑，接口定义如下：  

```python
class TodoManager:
    def __init__(self):
        """初始化待办管理器，维护内部待办列表和自增ID"""
        self.todos: list[dict] = []
        self._next_id: int = 1

    def add_todo(self, content: str) -> int:
        """
        添加新待办事项
        
        Args:
            content: 待办内容（非空字符串）
            
        Returns:
            新待办的唯一ID（整数）
            
        Raises:
            ValueError: 当content为空或仅含空白字符时抛出
        """
        if not content.strip():
            raise ValueError("待办内容不能为空")
        todo = {"id": self._next_id, "content": content.strip(), "completed": False}
        self.todos.append(todo)
        self._next_id += 1
        return todo["id"]

    def delete_todo(self, todo_id: int) -> bool:
        """
        根据ID删除待办
        
        Args:
            todo_id: 待删除的待办ID
            
        Returns:
            成功删除返回True，ID不存在返回False
        """
        for idx, todo in enumerate(self.todos):
            if todo["id"] == todo_id:
                self.todos.pop(idx)
                return True
        return False

    def get_all_todos(self) -> list[dict]:
        """
        获取所有待办列表
        
        Returns:
            待办列表（每个元素为字典：{id: int, content: str, completed: bool}）
        """
        return [todo.copy() for todo in self.todos]  # 返回副本避免外部修改内部状态

    def mark_todo_completed(self, todo_id: int) -> bool:
        """
        标记待办为已完成
        
        Args:
            todo_id: 待标记的待办ID
            
        Returns:
            成功标记返回True，ID不存在返回False
        """
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = True
                return True
        return False
```


## 4. pytest格式验收用例  
假设核心逻辑类在`todo_manager.py`中，验收用例覆盖所有功能点及边界场景：  

```python
import pytest
from todo_manager import TodoManager


def test_add_todo_normal():
    """测试正常添加待办"""
    manager = TodoManager()
    todo_id = manager.add_todo("Buy milk")
    assert todo_id == 1
    todos = manager.get_all_todos()
    assert len(todos) == 1
    assert todos[0]["content"] == "Buy milk"
    assert todos[0]["completed"] is False


def test_add_todo_empty_content():
    """测试添加空内容抛出异常"""
    manager = TodoManager()
    with pytest.raises(ValueError):
        manager.add_todo("")
    with pytest.raises(ValueError):
        manager.add_todo("   ")


def test_delete_todo_exist():
    """测试删除存在的待办"""
    manager = TodoManager()
    todo_id = manager.add_todo("Task1")
    assert manager.delete_todo(todo_id) is True
    assert len(manager.get_all_todos()) == 0


def test_delete_todo_not_exist():
    """测试删除不存在的待办"""
    manager = TodoManager()
    assert manager.delete_todo(999) is False


def test_get_all_todos_empty():
    """测试初始状态下获取待办列表为空"""
    manager = TodoManager()
    assert manager.get_all_todos() == []


def test_get_all_todos_multiple():
    """测试获取多个待办"""
    manager = TodoManager()
    manager.add_todo("Task A")
    manager.add_todo("Task B")
    todos = manager.get_all_todos()
    assert len(todos) == 2
    assert todos[0]["content"] == "Task A"
    assert todos[1]["content"] == "Task B"


def test_mark_todo_completed_exist():
    """测试标记存在的待办为完成"""
    manager = TodoManager()
    todo_id = manager.add_todo("Finish homework")
    assert manager.mark_todo_completed(todo_id) is True
    assert manager.get_all_todos()[0]["completed"] is True


def test_mark_todo_completed_not_exist():
    """测试标记不存在的待办"""
    manager = TodoManager()
    assert manager.mark_todo_completed(100) is False


def test_integration_flow():
    """综合测试完整流程：添加→查看→标记→删除→查看"""
    manager = TodoManager()
    # 添加两个待办
    id1 = manager.add_todo("Go to gym")
    id2 = manager.add_todo("Read book")
    # 查看初始状态
    todos = manager.get_all_todos()
    assert len(todos) == 2
    # 标记id1为完成
    assert manager.mark_todo_completed(id1) is True
    # 删除id2
    assert manager.delete_todo(id2) is True
    # 最终状态验证
    final_todos = manager.get_all_todos()
    assert len(final_todos) ==1
    assert final_todos[0]["id"] == id1
    assert final_todos[0]["completed"] is True
```


## 5. 运行说明  
1. 将核心类保存为`todo_manager.py`  
2. 将测试用例保存为`test_todo_manager.py`  
3. 执行测试：`pytest test_todo_manager.py -v`  

所有测试用例应全部通过，确保功能符合需求。