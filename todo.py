import argparse
import json
import os
from datetime import datetime
from threading import Thread
from time import sleep
from plyer import notification
import winsound
import platform
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

# Initialize
console = Console()
TODO_FILE = "tasks.json"
ALERT_CHECK_INTERVAL = 60  # Check every minute

# --- Core Functions ---
def load_tasks():
    """Load tasks with error handling"""
    try:
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, 'r') as f:
                tasks = json.load(f)
                # Convert string dates to datetime objects
                for task in tasks:
                    if 'due_date' in task and task['due_date']:
                        task['due_datetime'] = datetime.strptime(task['due_date'], "%Y-%m-%d")
                return tasks
    except Exception as e:
        console.print(f"[red]Error loading tasks: {e}[/red]")
    return []

def alert_daemon():
    """Background thread for checking due tasks"""
    while True:
        tasks = load_tasks()
        now = datetime.now()
        
        for task in tasks:
            if not task['completed'] and 'due_datetime' in task:
                if now >= task['due_datetime']:
                    play_alert_sound()
                    show_urgent_notification(
                        f"⚠️ OVERDUE: {task['description']}",
                        f"Category: {task.get('category', 'No category')}\n"
                        f"Priority: {task.get('priority', 'No priority')}"
                    )
        sleep(ALERT_CHECK_INTERVAL)

def play_alert_sound():
    """Multi-platform alert sound"""
    try:
        if platform.system() == 'Windows':
            winsound.Beep(1000, 1000)  # Loud beep
        elif platform.system() == 'Darwin':
            os.system('afplay /System/Library/Sounds/Sosumi.aiff')
        else:
            os.system('spd-say "ALERT! Task due now!"')
    except:
        pass

def show_urgent_notification(title, message):
    """Persistent notification"""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='Todo Alarm',
            timeout=10,  # Longer display
            toast=True  # Windows persistent toast
        )
    except:
        console.print(f"[blink red]ALERT: {title}[/blink red]")

# --- Rich UI Components ---
def display_task_table():
    """Interactive table with sorting"""
    tasks = load_tasks()
    table = Table(title="📝 Your Tasks", show_lines=True)
    
    # Columns
    table.add_column("#", style="cyan")
    table.add_column("Task", style="magenta")
    table.add_column("Due Date", justify="right")
    table.add_column("Priority", justify="center")
    table.add_column("Status", justify="center")
    
    # Rows with conditional formatting
    for i, task in enumerate(sorted(tasks, key=lambda x: x.get('priority', 'low')), 1):
        due_date = task.get('due_date', '')
        status = "[green]✓" if task['completed'] else "[red]⌛"
        
        # Priority colors
        priority = task.get('priority', '')
        if priority == 'high':
            priority = f"[bold red]{priority}🔥"
        elif priority == 'medium':
            priority = f"[yellow]{priority}"
            
        table.add_row(
            str(i),
            task['description'],
            due_date,
            priority,
            status
        )
    
    console.print(
        Panel.fit(
            table,
            title="[bold]Todo Manager[/bold]",
            subtitle="Press Ctrl+C to exit",
            border_style="blue"
        )
    )

# --- TUI Mode ---
def interactive_mode():
    """Text-based user interface"""
    with Live(auto_refresh=False) as live:
        while True:
            display_task_table()
            user_input = input("\nCommand (add/complete/delete/quit): ").strip().lower()
            
            if user_input == 'quit':
                break
            elif user_input == 'add':
                # ... (interactive add logic)
                pass

# --- Main ---
if __name__ == "__main__":
    # Start alert daemon
    Thread(target=alert_daemon, daemon=True).start()
    
    # Start interactive UI
    interactive_mode()