from fastapi import FastAPI, HTTPException

from app.models import TaskCreate, TaskUpdate
from app import storage

app = FastAPI(title="Task API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def view_all_tasks():
    return storage.load_tasks()

@app.post("/tasks")
def create_task(task: TaskCreate):
    tasks = storage.load_tasks()

    if tasks:
        next_id = max(task["id"] for task in tasks) + 1
    else:
        next_id = 1

    new_task = {
        "id": next_id,
        "title": task.title,
        "description": task.description,
        "completed": False
    }

    tasks.append(new_task)
    storage.save_tasks(tasks)

    return new_task

@app.get("/tasks/{id}")
def get_one_task(id: int):
    tasks = storage.load_tasks()

    for task in tasks:
        if id == task["id"]:
            return task

    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{id}")
def update_task(id: int, task_update: TaskUpdate):
    tasks = storage.load_tasks()

    for task in tasks:
        if id == task["id"]:
            task["title"] = task_update.title
            task["description"] = task_update.description
            task["completed"] = task_update.completed

            storage.save_tasks(tasks)

            return task

    raise HTTPException(status_code=404, detail="Task not found.")

@app.delete("/tasks/{id}", status_code=204)
def delete_task(id:int):
    tasks = storage.load_tasks()

    for task in tasks:
        if id == task["id"]:
            tasks.remove(task)

            storage.save_tasks(tasks)

            return {"message": "Task deleted"}

    raise HTTPException(status_code=404, detail="Task not found.")