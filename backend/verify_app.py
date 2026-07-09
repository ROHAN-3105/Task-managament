import unittest
import sys
import os

# Ensure backend config is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app import app

class TaskFlowAppTestCase(unittest.TestCase):
    def setUp(self):
        # Configure application for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_login_page_renders(self):
        """Verify that the login landing page returns 200 OK"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to TaskFlow', response.data)
        self.assertIn(b'username', response.data)
        self.assertIn(b'password', response.data)
        self.assertIn(b'role', response.data)

    def test_root_redirects_to_login(self):
        """Verify that root URL redirects correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/login'))

    def test_dashboard_requires_login(self):
        """Verify that accessing dashboard unauthorized redirects to login"""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/login'))

    def test_employees_requires_login(self):
        """Verify that accessing employees directory unauthorized redirects to login"""
        response = self.client.get('/employees')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/login'))

    def test_tasks_requires_login(self):
        """Verify that accessing tasks board unauthorized redirects to login"""
        response = self.client.get('/tasks')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/login'))

    def test_task_add_requires_login(self):
        """Verify that creating tasks unauthorized redirects to login"""
        response = self.client.get('/task/add')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/login'))

if __name__ == '__main__':
    print("Running TaskFlow application unit tests...")
    unittest.main()
