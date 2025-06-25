import argparse
import json
import os

TODO_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TODO_FILE, 'w') as f:
        json.dump(tasks, f)

def add_task(description):
    tasks = load_tasks()
    tasks.append({"description": description, "completed": False})
    save_tasks(tasks)
    print(f"Added: {description}")

def list_tasks():
    tasks = load_tasks()
    for i, task in enumerate(tasks, 1):
        status = "✓" if task["completed"] else " "
        print(f"{i}. [{status}] {task['description']}")

def complete_task(index):
    tasks = load_tasks()
    if 1 <= index <= len(tasks):
        tasks[index-1]["completed"] = True
        save_tasks(tasks)
        print(f"Completed: {tasks[index-1]['description']}")
    else:
        print("Invalid task number")

def main():
    parser = argparse.ArgumentParser(description="Simple CLI Todo List")
    subparsers = parser.add_subparsers(dest="command")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("description", help="Task description")
    
    # List command
    subparsers.add_parser("list", help="List all tasks")
    
    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark task as complete")
    complete_parser.add_argument("index", type=int, help="Task number to complete")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_task(args.description)
    elif args.command == "list":
        list_tasks()
    elif args.command == "complete":
        complete_task(args.index)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()