# Add these new imports at the top
from plyer import notification
import winsound  # Windows
import os
import platform
from time import sleep

# ... (keep existing imports)

def play_sound():
    """Play system sound (cross-platform)"""
    try:
        if platform.system() == 'Windows':
            winsound.MessageBeep()
        elif platform.system() == 'Darwin':  # Mac
            os.system('afplay /System/Library/Sounds/Ping.aiff')
        else:  # Linux
            os.system('spd-say "task updated"')
    except:
        pass  # Fail silently if sound isn't available

def show_notification(title, message):
    """Show desktop notification"""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='Todo CLI',
            timeout=3
        )
    except:
        print(f"❗ {message}")  # Fallback to console

# Modify critical functions to add alerts
def add_task(description, due_date=None, category=None, priority=None):
    tasks = load_tasks()
    tasks.append({
        "description": description,
        "completed": False,
        "due_date": due_date,
        "category": category,
        "priority": priority
    })
    save_tasks(tasks)
    print(f"{Fore.GREEN}✓ Added: {description}")
    show_notification("Task Added", description)
    play_sound()

def complete_task(index):
    tasks = load_tasks()
    if 1 <= index <= len(tasks):
        tasks[index-1]["completed"] = True
        save_tasks(tasks)
        msg = f"Completed: {tasks[index-1]['description']}"
        print(f"{Fore.GREEN}✓ {msg}")
        show_notification("Task Completed!", msg)
        play_sound()
    else:
        print(f"{Fore.RED}✖ Invalid task number")