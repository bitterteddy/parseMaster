from enum import Enum
import threading
from typing import Any, Dict
from database import get_database

db = get_database()

class TaskStatuses(Enum):
    WAITING_TO_CREATE = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    PAUSED = 3
    STOPPED = 4
    ERROR = 5
    
class Task(d.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(120), nullable=False)
    task_type = db.Column(db.String(120), nullable=False)
    parameters = db.Column(db.Text, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    def __init__(self, task_id: int, status:str, task_type: str, parameters:str, user_id:int):
        self.task_id = task_id
        self.status = status
        self.type = task_type
        self.parameters = parameters
        self.result = None
        self.error_message = None
        self._lock = threading.Lock()
    
    def start(self):
        self.status = TaskStatuses.IN_PROGRESS.name
        print(f"Task {self.task_id} - in progress...")

    def complete(self, result: Any):
        self.status = TaskStatuses.COMPLETED.name
        self.result = result
        print(f"Task {self.task_id} - completed!")

    def fail(self, error_message: str):
        self.status = TaskStatuses.ERROR.name
        self.error_message = error_message
        print(f"Task {self.task_id} failed to complete! Error: {error_message}")

    def is_paused(self):
        return self.status == TaskStatuses.PAUSED.name
    
    def pause(self):
        with self._lock:
            self.status = TaskStatuses.PAUSED.name
            print(f"Task {self.task_id} - paused!")

    def resume(self):
        with self._lock:
            self.status = TaskStatuses.IN_PROGRESS.name
            print(f"Task {self.task_id} - resumed!")
            print(f"Task {self.task_id} - in progress...")

    def stop(self):
        with self._lock:
            self.status = TaskStatuses.STOPPED.name
            print(f"Task {self.task_id} - stopped!")

    def is_stopped(self):
        return self.status == TaskStatuses.STOPPED.name
    
    def get_parameters_as_dict(self) -> Dict[str, Any]: 
        return eval(self.parameters)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "type": self.type,
            "parameters": eval(self.parameters),
            "result": self.result,
            "error_message": self.error_message,
        }
    