import unittest
import os
import json
from unittest.mock import patch
from io import StringIO
import todo

class TestTodoApp(unittest.TestCase):
    def setUp(self):
        # Ensure no test file exists before each test
        if os.path.exists(todo.TODO_FILE):
            os.remove(todo.TODO_FILE)

    def tearDown(self):
        # Clean up after each test
        if os.path.exists(todo.TODO_FILE):
            os.remove(todo.TODO_FILE)

    def test_load_tasks_empty(self):
        tasks = todo.load_tasks()
        self.assertEqual(tasks, [])

    def test_save_and_load_tasks(self):
        test_tasks = [{"description": "Test task", "completed": False}]
        todo.save_tasks(test_tasks)
        loaded_tasks = todo.load_tasks()
        self.assertEqual(loaded_tasks, test_tasks)

    @patch('sys.stdout', new_callable=StringIO)
    def test_add_task(self, mock_stdout):
        todo.add_task("New task")
        tasks = todo.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["description"], "New task")
        self.assertFalse(tasks[0]["completed"])
        self.assertIn("Added: New task", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_list_tasks_empty(self, mock_stdout):
        todo.list_tasks()
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, "")

    @patch('sys.stdout', new_callable=StringIO)
    def test_list_tasks_with_items(self, mock_stdout):
        test_tasks = [
            {"description": "Task 1", "completed": False},
            {"description": "Task 2", "completed": True}
        ]
        todo.save_tasks(test_tasks)
        todo.list_tasks()
        output = mock_stdout.getvalue()
        self.assertIn("[ ] Task 1", output)
        self.assertIn("[✓] Task 2", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_complete_task_valid(self, mock_stdout):
        test_tasks = [{"description": "Task 1", "completed": False}]
        todo.save_tasks(test_tasks)
        todo.complete_task(1)
        tasks = todo.load_tasks()
        self.assertTrue(tasks[0]["completed"])
        self.assertIn("Completed: Task 1", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_complete_task_invalid(self, mock_stdout):
        test_tasks = [{"description": "Task 1", "completed": False}]
        todo.save_tasks(test_tasks)
        todo.complete_task(2)  # Invalid index
        tasks = todo.load_tasks()
        self.assertFalse(tasks[0]["completed"])
        self.assertIn("Invalid task number", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()