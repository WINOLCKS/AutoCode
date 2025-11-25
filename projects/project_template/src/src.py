```python
class TodoManager:
    def __init__(self):
        self.todos: list[dict] = []
        self._next_id: int = 1

    def add_todo(self, content: str) -> int:
        if not content.strip():
            raise ValueError("待办内容不能为空")
        todo = {"id": self._next_id, "content": content.strip(), "completed": False}
        self.todos.append(todo)
        self._next_id += 1
        return todo["id"]

    def delete_todo(self, todo_id: int) -> bool:
        for idx, todo in enumerate(self.todos):
            if todo["id"] == todo_id:
                self.todos.pop(idx)
                return True
        return False

    def get_all_todos(self) -> list[dict]:
        return [todo.copy() for todo in self.todos]

    def mark_todo_completed(self, todo_id: int) -> bool:
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = True
                return True
        return False
```