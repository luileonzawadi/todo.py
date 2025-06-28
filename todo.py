import json, os, platform
from datetime import datetime
from threading import Thread
from time import sleep
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from plyer import notification
import winsound
from ttkthemes import ThemedTk

TODO_FILE = "tasks.json"
ALERT_CHECK_INTERVAL = 60

# Load and save
def load_tasks():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as f:
            tasks = json.load(f)
            for task in tasks:
                if 'due_date' in task:
                    try:
                        task['due_datetime'] = datetime.strptime(task['due_date'], "%Y-%m-%d")
                    except:
                        task['due_datetime'] = None
            return tasks
    return []

def save_tasks(tasks):
    for task in tasks:
        if 'due_datetime' in task:
            task['due_date'] = task['due_datetime'].strftime("%Y-%m-%d")
            del task['due_datetime']
    with open(TODO_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

# Alerts
def play_alert_sound():
    try:
        if platform.system() == 'Windows':
            winsound.Beep(1000, 1000)
        elif platform.system() == 'Darwin':
            os.system('afplay /System/Library/Sounds/Sosumi.aiff')
        else:
            os.system('spd-say "Task due now!"')
    except:
        pass

def show_urgent_notification(title, message):
    try:
        notification.notify(
            title=title, message=message, app_name="Todo Alert",
            timeout=10, toast=True
        )
    except:
        print(f"Notification error: {title}")

def alert_daemon():
    while True:
        tasks = load_tasks()
        now = datetime.now()
        for task in tasks:
            if not task['completed'] and 'due_datetime' in task:
                if now >= task['due_datetime']:
                    play_alert_sound()
                    show_urgent_notification(
                        f"⚠️ OVERDUE: {task['description']}",
                        f"Category: {task.get('category', 'N/A')}\nPriority: {task.get('priority', 'N/A')}"
                    )
        sleep(ALERT_CHECK_INTERVAL)

# App
class TodoApp(ThemedTk):
    def __init__(self):
        super().__init__(theme="black")
        self.title("Todo Manager")
        self.geometry("800x500")
        self.tasks = load_tasks()
        self.filtered_category = None
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # Filter + dark toggle
        top_frame = tk.Frame(self)
        top_frame.pack(fill='x', pady=5)
        
        tk.Label(top_frame, text="Filter by Category:", fg="white", bg="black").pack(side=tk.LEFT, padx=10)
        self.cat_filter = ttk.Combobox(top_frame, values=self.get_all_categories(), state='readonly')
        self.cat_filter.pack(side=tk.LEFT)
        self.cat_filter.bind("<<ComboboxSelected>>", lambda e: self.filter_by_category())

        tk.Button(top_frame, text="Clear Filter", command=self.clear_filter).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Toggle Dark Mode", command=self.toggle_theme).pack(side=tk.RIGHT, padx=10)

        # Table
        columns = ("Task", "Due Date", "Priority", "Category", "Status")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.tree.bind("<Button-3>", self.show_context_menu)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Task", command=self.add_task).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Mark Completed", command=self.mark_completed).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Task", command=self.delete_task).pack(side=tk.LEFT, padx=5)

    def get_all_categories(self):
        return sorted(set(task.get('category', '') for task in self.tasks if task.get('category')))

    def filter_by_category(self):
        self.filtered_category = self.cat_filter.get()
        self.refresh_table()

    def clear_filter(self):
        self.filtered_category = None
        self.cat_filter.set('')
        self.refresh_table()

    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for task in self.tasks:
            if self.filtered_category and task.get('category') != self.filtered_category:
                continue
            status = "✓ Done" if task['completed'] else "⌛ Pending"
            prio = task.get('priority', 'low').lower()
            self.tree.insert(
                '', 'end',
                values=(task['description'], task.get('due_date', ''), prio, task.get('category', ''), status),
                tags=(prio,)
            )

        self.tree.tag_configure('high', foreground='red')
        self.tree.tag_configure('medium', foreground='orange')
        self.tree.tag_configure('low', foreground='green')

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="Edit Task", command=self.edit_task)
            menu.tk_popup(event.x_root, event.y_root)

    def add_task(self):
        self.task_form_popup("Add Task")

    def edit_task(self):
        selected = self.tree.selection()
        if not selected:
            return
        desc = self.tree.item(selected[0])['values'][0]
        task = next((t for t in self.tasks if t['description'] == desc), None)
        if task:
            self.task_form_popup("Edit Task", task)

    def task_form_popup(self, title, task=None):
        def save_new_task():
            desc = desc_entry.get().strip()
            due_dt = due_date.get_date()
            prio = priority_var.get()
            cat = cat_entry.get().strip()

            if not desc:
                messagebox.showerror("Error", "Description is required.")
                return

            if task:  # edit
                task['description'] = desc
                task['due_date'] = due_dt.strftime("%Y-%m-%d")
                task['priority'] = prio
                task['category'] = cat or "General"
                task['due_datetime'] = due_dt
            else:
                self.tasks.append({
                    "description": desc,
                    "due_date": due_dt.strftime("%Y-%m-%d"),
                    "priority": prio,
                    "category": cat or "General",
                    "completed": False,
                    "due_datetime": due_dt
                })

            save_tasks(self.tasks)
            self.refresh_table()
            popup.destroy()

        popup = tk.Toplevel(self)
        popup.title(title)
        popup.geometry("350x300")
        popup.resizable(False, False)

        tk.Label(popup, text="Description:").pack(anchor='w', padx=10, pady=(10, 0))
        desc_entry = tk.Entry(popup, width=40)
        desc_entry.pack(padx=10)
        desc_entry.insert(0, task['description'] if task else '')

        tk.Label(popup, text="Due Date:").pack(anchor='w', padx=10, pady=(10, 0))
        due_date = DateEntry(popup, width=18, date_pattern='yyyy-mm-dd')
        due_date.pack(padx=10)
        if task:
            due_date.set_date(datetime.strptime(task['due_date'], "%Y-%m-%d"))

        tk.Label(popup, text="Priority:").pack(anchor='w', padx=10, pady=(10, 0))
        priority_var = tk.StringVar(value=task['priority'] if task else "low")
        tk.OptionMenu(popup, priority_var, "high", "medium", "low").pack(padx=10)

        tk.Label(popup, text="Category:").pack(anchor='w', padx=10, pady=(10, 0))
        cat_entry = tk.Entry(popup, width=30)
        cat_entry.pack(padx=10)
        cat_entry.insert(0, task.get('category', '') if task else '')

        tk.Button(popup, text="Save Task", command=save_new_task).pack(pady=15)

    def mark_completed(self):
        selected = self.tree.selection()
        if not selected:
            return
        desc = self.tree.item(selected[0])['values'][0]
        for task in self.tasks:
            if task['description'] == desc:
                task['completed'] = True
        save_tasks(self.tasks)
        self.refresh_table()

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            return
        desc = self.tree.item(selected[0])['values'][0]
        self.tasks = [t for t in self.tasks if t['description'] != desc]
        save_tasks(self.tasks)
        self.refresh_table()

    def toggle_theme(self):
        current = self.get_theme()
        self.set_theme("arc" if current == "black" else "black")

# Run
if __name__ == "__main__":
    Thread(target=alert_daemon, daemon=True).start()
    app = TodoApp()
    app.mainloop()
