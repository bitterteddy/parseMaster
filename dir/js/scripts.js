function showFieldsByType() {
    const taskType = document.getElementById('task-type').value;
    document.getElementById('css-fields').classList.toggle('d-none', taskType !== 'parse');
    document.getElementById('regex-fields').classList.toggle('d-none', taskType !== 'regex_parse');
}

function addCSSField() {
    const container = document.getElementById('css-parameters-container');
    const field = `
        <div class="parameter-group mb-3">
            <div class="row g-2">
                <div class="col-md-4">
                    <label class="form-label">Name:</label>
                    <input type="text" name="name" class="form-control" placeholder="Name">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Selector:</label>
                    <input type="text" name="selector" class="form-control" placeholder="CSS Selector">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Attribute:</label>
                    <select name="attribute" class="form-select">
                        <option value="text">Text</option>
                        <option value="href">Href</option>
                        <option value="src">Src</option>
                        <option value="alt">Alt</option>
                        <option value="title">Title</option>
                        <option value="id">ID</option>
                        <option value="class">Class</option>
                        <option value="">None</option>
                    </select>
                </div>
                <div class="col-md-2 mt-2">
                    <label class="form-label">Multiple:</label>
                    <input type="checkbox" name="multiple" class="form-check-input ms-2">
                </div>
            </div>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', field);
}

function addRegexPattern() {
    const container = document.getElementById('regex-patterns');
    const field = `
        <div class="input-group mb-2">
            <input type="text" class="form-control" placeholder="Enter regex pattern" name="regex_pattern">
        </div>
    `;
    container.insertAdjacentHTML('beforeend', field);
}

async function submitTask() {
    const taskType = document.getElementById("task-type").value;
    const urls = document.getElementById("urls").value.split("\n").filter(url => url.trim());
    let parameters = {};

    if (taskType === "parse") {
        const container_selector = document.getElementById("container-selector").value
        const fields = document.querySelectorAll("#css-parameters-container .parameter-group");
        const elements = Array.from(fields).map(field => ({
            name: field.querySelector("input[name='name']").value,
            selector: field.querySelector("input[name='selector']").value,
            attribute: field.querySelector("select[name='attribute']").value,
            multiple: field.querySelector("input[name='multiple']").checked
        }));
        parameters.parse_parameters = { 
            container_selector: container_selector,
            elements 
        };
    } else if (taskType === "regex_parse") {
        const regexFields = document.querySelectorAll("#regex-fields input[name='regex_pattern']");
        const regexPatterns = Array.from(regexFields).map(input => input.value);
        parameters.regex_patterns = regexPatterns;
    }

    const response = await fetch("/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            task_type: taskType,
            parameters: { urls, ...parameters }
        })
    });

    const result = await response.json();
    alert(result.message);
    // loadTasks();
}

async function loadTasks() {
    try {
        const response = await fetch('/tasks');  
        const tasks = await response.json();  

        const tasksList = document.getElementById('tasks-list');
        tasksList.innerHTML = '';  

        tasks.forEach(task => {
            const li = document.createElement('li');
            console.log(task);
            li.innerHTML = `
                <span>Task ${task.id}: ${task.status}</span>
                <div class="task-actions">
                    <button class="start" onclick="startTask(${task.id})">Start</button>
                    <button class="stop" onclick="stopTask(${task.id})">Stop</button>
                    <button class="view" onclick="viewTaskDetails(${task.id})" data-bs-toggle="modal" data-bs-target="#viewModal${task.id}">View Details</button>
                    
                    <div class="modal fade" id="viewModal${task.id}" tabindex="-1" aria-labelledby="taskModalLabel" aria-hidden="true">
                        <div class="modal-dialog">
                             <span>Task ${task.id}: ${task.status}</span>
                            <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="taskModalLabel">Task ${task.id} Details</
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <pre id="task-details${task.id}"></pre>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            </div>
                            </div>
                        </div>
                    </div>

                    
                    <button class="view" onclick="viewTaskResult(${task.id})" data-bs-toggle="modal" data-bs-target="#resultModal${task.id}">View Result</button>

                    <div class="modal fade" id="resultModal${task.id}" tabindex="-1" aria-labelledby="resultModalLabel" aria-hidden="true">
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="resultModalLabel">Task Result ${task.id}</h5>
                                    <button class="btn btn-primary" onclick="downloadJSON(${task.id})">Download JSON</button>
                                    <button class="btn btn-secondary" onclick="downloadCSV(${task.id})">Download CSV</button>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <table class="table">
                                        <thead id="resultTableHead${task.id}">
                                            <!-- Заголовки таблицы будут добавлены сюда -->
                                        </thead>
                                        <tbody id="resultTableBody${task.id}">
                                            <!-- Данные таблицы будут добавлены сюда -->
                                        </tbody>
                                    </table>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            tasksList.appendChild(li); 
        });
    } catch (error) {
        console.error('Error fetching tasks:', error);
    }
}

window.onload = loadTasks;

function viewTaskDetails(taskId) {
    console.log(taskId);

    fetch(`/task/${taskId}`)
      .then(response => {
        console.log(response);

        if (!response.ok) {
          throw new Error('Task not found');
        }
        return response.json();
      })
      .then(task => {
        console.log(task);
        const taskDetails = document.getElementById("task-details"+taskId);
  
        taskDetails.textContent = JSON.stringify(task, null, 2);
      })
      .catch(error => {
        const taskDetails = document.getElementById("task-details"+taskId);
        taskDetails.textContent = `Error: ${error.message}`;
      });
}

function startTask(taskId) {
    fetch(`/tasks/${taskId}/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          alert(`Error: ${data.error}`);
        } else {
          alert(`Success: ${data.message}`);
        }
      })
      .catch(error => {
        alert(`Unexpected error: ${error.message}`);
      });
}

async function viewTaskResult(taskId) {
    try {
        const response = await fetch(`/tasks/${taskId}/result`);
        if (!response.ok) {
            throw new Error(`Error fetching task result: ${response.statusText}`);
        }

        const data = await response.json();
        const rows = data
        const columns = Object.keys(rows[0] || {}); 
        
        const tableHead = document.getElementById("resultTableHead"+taskId);
        const tableBody = document.getElementById("resultTableBody"+taskId);

        tableHead.innerHTML = "";
        tableBody.innerHTML = "";

        const headRow = document.createElement("tr");
        columns.forEach(column => {
            const th = document.createElement("th");
            th.textContent = column.replace('_', ' ').toUpperCase();
            headRow.appendChild(th);
        });
        tableHead.appendChild(headRow);

        rows.forEach(row => {
            const bodyRow = document.createElement("tr");
            columns.forEach(column => {
                const td = document.createElement("td");
                td.textContent = row[column] || "";
                bodyRow.appendChild(td);
            });
            tableBody.appendChild(bodyRow);
        });

        const modal = new bootstrap.Modal(document.getElementById(`resultModal${taskId}`));
        modal.show();

    } catch (error) {
        console.error(error);
        alert("Failed to load task result. Please try again later.");
    }
}

async function downloadJSON(taskId) {
    try {
        const response = await fetch(`/tasks/${taskId}/result_in_json`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch task result file');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `parsing_task_${taskId}_result.json`; 
        a.click(); 

        URL.revokeObjectURL(url);
    }
    catch (error) {
        console.error('Error downloading JSON file:', error);
    }
}

async function downloadCSV(taskId) {
    try {
        const response = await fetch(`/tasks/${taskId}/result_in_csv`);

        if (!response.ok) {
            throw new Error('Failed to fetch task result file');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `parsing_task_${taskId}_result.csv`;
        a.click(); 

        URL.revokeObjectURL(url);
    }
    catch (error) {
        console.error('Error downloading CSV file:', error);
    }
}

loadTasks();