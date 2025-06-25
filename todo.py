import argparse
import json
import os
from datetime import datetime
from colorama import Fore, init, Style

init(autoreset=True)  # Auto-reset colors after each print

TODO_FILE = "tasks.json"
BACKUP_FILE = "tasks_backup.json"

def load_tasks():
    """Load tasks from JSON file, return empty list if file doesn't exist."""
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_tasks(tasks):
    """Save tasks to JSON file with indentation."""
    with open(TODO_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def backup_tasks():
    """Create a backup of current tasks."""
    tasks = load_tasks()
    with open(BACKUP_FILE, 'w') as f:
        json.dump(tasks, f)

def add_task(description, due_date=None, category=None, priority=None):
    """Add a new task with optional metadata."""
    tasks = load_tasks()
    tasks.append({
        "description": description,
        "completed": False,
        "due_date": due_date,
        "category": category,
        "priority": priority,
        "created_at": datetime.now().isoformat()
    })
    save_tasks(tasks)
    print(f"{Fore.GREEN}✓ Added: {description}")

def list_tasks(filter_category=None, hide_completed=False, priority=None):
    """Display tasks with colorful formatting and filters."""
    tasks = load_tasks()
    for i, task in enumerate(tasks, 1):
        # Apply filters
        if filter_category and task.get("category") != filter_category:
            continue
        if hide_completed and task["completed"]:
            continue
        if priority and task.get("priority") != priority:
            continue

        # Color coding
        status = f"{Fore.GREEN}✓" if task["completed"] else " "
        priority_color = {
            "high": Fore.RED,
            "medium": Fore.YELLOW,
            "low": Fore.BLUE
        }.get(task.get("priority"), "")
        priority_text = f"{priority_color}⬆" if task.get("priority") else ""
        
        due_text = (
            f"{Fore.YELLOW}(Due: {task['due_date']})" 
            if task.get("due_date") else ""
        )
        category_text = (
            f"{Fore.CYAN}[{task['category']}]" 
            if task.get("category") else ""
        )

        print(
            f"{i}. [{status}] {priority_text} {task['description']} "
            f"{due_text} {category_text}"
        )

def complete_task(index):
    """Mark a task as completed."""
    tasks = load_tasks()
    if 1 <= index <= len(tasks):
        tasks[index-1]["completed"] = True
        save_tasks(tasks)
        print(f"{Fore.GREEN}✓ Completed: {tasks[index-1]['description']}")
    else:
        print(f"{Fore.RED}✖ Invalid task number")

def delete_task(index):
    """Delete a task permanently."""
    tasks = load_tasks()
    if 1 <= index <= len(tasks):
        deleted = tasks.pop(index-1)
        save_tasks(tasks)
        print(f"{Fore.RED}✖ Deleted: {deleted['description']}")
    else:
        print(f"{Fore.RED}✖ Invalid task number")

def undo_last_action():
    """Restore tasks from backup."""
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, 'r') as f:
            tasks = json.load(f)
        save_tasks(tasks)
        print(f"{Fore.GREEN}✓ Undo successful!")
    else:
        print(f"{Fore.RED}✖ No backup found")

def main():
    """CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description=f"{Fore.CYAN}✨ Enhanced Todo CLI{Style.RESET_ALL}",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command")

    # Add
    add_parser = subparsers.add_parser("add", help="Add a task")
    add_parser.add_argument("description", help="Task description")
    add_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
    add_parser.add_argument("--category", help="Task category")
    add_parser.add_argument(
        "--priority", 
        choices=["high", "medium", "low"],
        help="Priority level"
    )

    # List
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument(
        "--hide-completed", 
        action="store_true",
        help="Hide completed tasks"
    )
    list_parser.add_argument(
        "--priority",
        choices=["high", "medium", "low"],
        help="Filter by priority"
    )

    # Complete
    complete_parser = subparsers.add_parser("complete", help="Mark task complete")
    complete_parser.add_argument("index", type=int, help="Task number")

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("index", type=int, help="Task number")

    # Undo
    subparsers.add_parser("undo", help="Undo last change")

    args = parser.parse_args()

    # Backup before destructive actions
    if args.command in ["complete", "delete", "add"]:
        backup_tasks()

    if args.command == "add":
        add_task(args.description, args.due, args.category, args.priority)
    elif args.command == "list":
        list_tasks(args.category, args.hide_completed, args.priority)
    elif args.command == "complete":
        complete_task(args.index)
    elif args.command == "delete":
        delete_task(args.index)
    elif args.command == "undo":
        undo_last_action()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()