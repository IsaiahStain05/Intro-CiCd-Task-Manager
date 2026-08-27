import json
from pathlib import Path
import os

TASKS_FILE = Path(
    os.getenv("TASKS_FILE", "app/tasks.json")
)

def load_tasks(file_path=None):
    if file_path is None:
        file_path = TASKS_FILE

    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("[]")

    with open(file_path, "r") as file:
        return json.load(file)


def save_tasks(tasks, file_path=None):
    if file_path is None:
        file_path = TASKS_FILE

    with open(file_path, "w") as file:
        json.dump(tasks, file, indent=2)