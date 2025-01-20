from concurrent.futures import ThreadPoolExecutor
import threading
from flask import Flask, jsonify, render_template, request
from sqlalchemy import select
from models.database import add_item, create_custom_table, fill_custom_table, get_item, get_item_by_id, get_items, get_items_as_dicts, initialize, update_item
from models.task import Task, TaskStatuses
from models.user import User
from parse_methods.soup_parser import SoupParser
from parse_methods.regex_parser import RegexParser
import json

app = Flask(__name__, static_folder="dir", template_folder="dir/templates")
app = initialize(app, "parse_Master")

task_lock = threading.Lock()
executor = ThreadPoolExecutor(max_workers=5)

def run_task(task_id):
    try:
        all_results = []
        task = get_item_by_id(app, Task, task_id)
        
        if not task:
            raise Exception("Task not found")
        
        # try:
        #     parameters = (
        #         json.loads(task.parameters)
        #         if isinstance(task.parameters, str)
        #         else task.parameters
        #     )
        # except Exception as e:
        #     raise Exception(f"Error parsing parameters: {str(e)}")

        parameters = json.loads(task.parameters)
        if not task.create_results_table(app):
            raise ValueError("Cant buid results' table")
        # parameters = task.get_parameters_as_dict()
        # print(parameters)
        if task.task_type == "parse":
            parser = SoupParser()
            urls = parameters.get("urls", [])
            parse_parameters = parameters.get("parse_parameters", {})
        elif task.task_type == "regex_parse":
            parser = RegexParser()
            urls = parameters.get("urls", [])
            regex_parameters = parameters.get("regex_patterns", [])
        else:
            raise ValueError("Unknown task type")
        
        # all_results = []
        for url in urls:
            try:
                if task.status == TaskStatuses.STOPPED.name:
                    print(f"Task {task.id} stopped.")
                    break
                if task.status == TaskStatuses.PAUSED.name:
                    print(f"Task {task.id} paused. Skipping URL: {url}")
                    continue
                result = None
                if task.task_type == "parse":
                    result = parser.parse(url, parse_parameters)
                elif task.task_type == "regex_parse":
                    result = parser.parse(url, {"regex_patterns": regex_parameters})
                if result:
                    task.save_result(app, result)
                # all_results.extend(result)

            except Exception as e:
                print(f"Error parsing URL {url} for task {task.id} ({task.task_type}): {str(e)}")

        # if all_results:
        #     table_name = f"parsed_results_{task_id}"
        #     print(table_name)
        #     # elements = json.loads(parameters).get("elements", [])
        #     elements = parameters.get("parse_parameters", {}).get("elements", [])

        #     if(elements):
        #         create_custom_table(app, table_name, elements)
        #         fill_custom_table(app, table_name, all_results)

    except Exception as e:
        fail_lambda = lambda t, m: t.fail(m)
        update_item(app, task, fail_lambda, str(e))
        print(f"Error during task execution: {str(e)}")


@app.route("/")
def index():
    try:
        print("Rendering index.html")
        return render_template("index.html")
    except Exception as e:
        print(f"Error rendering template: {str(e)}")
        return str(e)

@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        # try:
        #     u = User(name = "admin", mail = "fff@gmail.com", pswrd = "123")
        # except Exception as e:
        #     print("Error creating user", e)
        # print(u)
        # try:
        #     add_item(app, u)
        # except:
        #     print("SOmething went wrong")
        # try:
        #     user = get_item_by_id(app, User, id=1)
        # except Exception as e:
        #     print("Error finding user", e)

        user = get_item_by_id(app, User, id=1)
        # print(user.id)
        data = request.json
        print(data)
        type_value = data.get('task_type')
        print(type_value)
        parameters = data.get('parameters', {})

        if not type_value or not isinstance(parameters, dict):
            return jsonify({"error": "Invalid input"}), 400

        pars=json.dumps(parameters)
        new_task = Task(user_id=user.id, task_type="parse", parameters=pars, status=TaskStatuses.WAITING_TO_CREATE.name)
        print(f"Task state before insert: {new_task.__dict__}")
        add_item(app, new_task)

        return jsonify({"message": "Task created"})
    except Exception as e:
        return jsonify({"error": f"Error creating task: {str(e)}"}), 500

@app.route('/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        task = get_item_by_id(app, Task, task_id)
        
        if task is None:
            return jsonify({"error": "Task not found"}), 404

        return jsonify(task.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/tasks', methods=['GET'])
def get_all():
    try:
        statement = select(Task)
        tasks_data = get_items(app, statement)
        if not tasks_data:
            return jsonify({"message": "No tasks found"}), 404
        res = [i.to_dict() for i in tasks_data]        
        return jsonify(res), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching tasks: {str(e)}"}), 500

@app.route('/tasks/<int:task_id>/start', methods=['POST'])
def start_task(task_id):
    try: 
        with app.app_context():
            task = get_item_by_id(app, Task, task_id)
            if not task:
                return jsonify({"error": "Task not found"}), 404
            
            if task.status not in [TaskStatuses.WAITING_TO_CREATE.name, TaskStatuses.PAUSED.name, TaskStatuses.IN_PROGRESS.name, TaskStatuses.ERROR.name]:
                return jsonify({"error": f"Task {task.id} cannot be started."}), 400
            
            setter_lambda = lambda t, s: t.change_status(s)
            update_item(app, task, setter_lambda, TaskStatuses.IN_PROGRESS.name)
            
        threading.Thread(target=run_task, args=(task_id,)).start()
        
        return jsonify({"message": f"Task {task_id} started."})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(host='localhost', port=5001,debug=True)