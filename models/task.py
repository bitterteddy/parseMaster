from enum import Enum
import json
import threading
from typing import Any, Dict
from models.database import create_custom_table, fill_custom_table, get_database

db = get_database()

class TaskStatuses(Enum):
    WAITING_TO_CREATE = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    PAUSED = 3
    STOPPED = 4
    ERROR = 5
    
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(120), nullable=False)
    task_type = db.Column(db.String(120), nullable=False, default="parse")
    parameters = db.Column(db.Text, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    def __init__(self, status:str, task_type, parameters:str, user_id:int):
        self.status = status
        self.type = task_type
        self.parameters = parameters
        self.result = None
        self.error_message = None
        self.user_id = user_id
        self._lock = threading.Lock()
        self.setter_lambda = lambda t, s: t.change_status(s)
        self.fail_lambda = lambda t, m: t.fail(m)
    
    def change_status(self, status):
        self.status = status
    
    # # def start(self):
    # #     self.status = TaskStatuses.IN_PROGRESS.name
    # #     print(f"Task {self.id} - in progress...")

    def complete(self, result: Any):
        self.status = TaskStatuses.COMPLETED.name
        self.result = result
        print(f"Task {self.id} - completed!")

    def fail(self, error_message: str):
        self.status = TaskStatuses.ERROR.name
        self.error_message = error_message
        # print(f"Task {self.id} failed to complete! Error: {error_message}")

    def is_paused(self):
        return self.status == TaskStatuses.PAUSED.name
    
    def pause(self):
        with self._lock:
            self.status = TaskStatuses.PAUSED.name
            print(f"Task {self.id} - paused!")

    def resume(self):
        with self._lock:
            self.status = TaskStatuses.IN_PROGRESS.name
            print(f"Task {self.id} - resumed!")
            print(f"Task {self.id} - in progress...")

    def stop(self):
        with self._lock:
            self.status = TaskStatuses.STOPPED.name
            print(f"Task {self.id} - stopped!")

    def is_stopped(self):
        return self.status == TaskStatuses.STOPPED.name
    
    def get_parameters_as_dict(self) -> Dict[str, Any]: 
        return eval(self.parameters)
    
    def create_results_table(self, app):
        table_name = f"parsed_results_{self.id}"
        pars = json.loads(self.parameters)
        elements = pars.get("parse_parameters", {}).get("elements", [])
        if(elements):
            create_custom_table(app, table_name, elements)
            return True
        else:
            return False    
            
    def save_result(self, app, result):
        table_name = f"parsed_results_{self.id}"
        fill_custom_table(app, table_name, [result])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status,
            "task_type": self.task_type,
            "parameters": self.parameters,
            "error_message": self.error_message,
            "user_id": self.user_id
        }
    