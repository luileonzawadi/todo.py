import unittest
import os
import json
from unittest.mock import patch
from io import StringIO
import todo

class TestTodoApp(unittest.TestCase):
    def setUp(self):
        self.test_file = todo.TODO_FILE
        self.backup_file = todo.BACKUP_FILE
        self.cleanup_files()

    def tearDown(self):
        self.cleanup_files()

    def cleanup_files(self):
        for file in [self.test_file, self.backup_file]:
            if os.path.exists(file):
                os.remove(file)

    def test_add_task_with_metadata(self):
        todo.add_task("Test", due_date="2024-12-31", category="work", priority="high")
        tasks = todo.load_tasks()
        self.assertEqual(tasks[0]["description"], "Test")
        self.assertEqual(tasks[0]["category"], "work")
        self.assertEqual(tasks[0]["priority"], "high")

    @patch('sys.stdout', new_callable=StringIO)
    def test_undo_functionality(self, mock_stdout):
        # Add and then undo
        todo.add_task("Test undo")
        todo.undo_last_action()
        self.assertIn("Undo successful", mock_stdout.getvalue())
        self.assertEqual(len(todo.load_tasks()), 0)

    def test_priority_filter(self):
        todo.add_task("Urgent", priority="high")
        todo.add_task("Normal", priority="medium")
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            todo.list_tasks(priority="high")
            output = mock_stdout.getvalue()
            self.assertIn("Urgent", output)
            self.assertNotIn("Normal", output)

if __name__ == '__main__':
    unittest.main()