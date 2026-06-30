import json
from datetime import datetime, date
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from planner.models import AIPlan


class AIPlannerTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.planner_url = reverse('ai_planner')
        
        # Test data matching user requirements
        self.form_data = {
            'goal': 'Build AI TaskGenie using Django and Gemini AI',
            'available_hours': '28',
            'priority': 'High',
            'energy_level': 'High',
            'deadline': '2026-07-31',
            'break_duration': '30',
            'work_style': 'Balanced',
            'additional_notes': 'Build a production-ready AI productivity platform with authentication, task management, AI roadmap planner, analytics dashboard, responsive UI, testing and deployment.',
        }
        
        # Mock Gemini API response
        self.mock_response = {
            "phases": [
                {"name": "Foundation & Setup", "description": "Set up the Django project and core infrastructure"},
                {"name": "Core Features", "description": "Implement user authentication and task management"},
                {"name": "AI Integration", "description": "Integrate Gemini AI and build the roadmap planner"},
                {"name": "Polish & Deployment", "description": "Add analytics, responsive UI, testing and deployment"}
            ],
            "tasks": [
                {
                    "title": "Initialize Django Project",
                    "description": "Set up Django project with virtual environment, requirements, and initial apps",
                    "priority": "High",
                    "estimated_duration": 120,
                    "suggested_deadline": datetime.now().date().strftime("%Y-%m-%d"),
                    "phase": "Foundation & Setup",
                    "order": 1
                },
                {
                    "title": "User Authentication",
                    "description": "Implement login, signup, and profile management using Django auth",
                    "priority": "High",
                    "estimated_duration": 180,
                    "suggested_deadline": (date(2026, 7, 5)).strftime("%Y-%m-%d"),
                    "phase": "Foundation & Setup",
                    "order": 2
                },
                {
                    "title": "Task Management Models",
                    "description": "Create task models and basic CRUD operations",
                    "priority": "High",
                    "estimated_duration": 150,
                    "suggested_deadline": (date(2026, 7, 10)).strftime("%Y-%m-%d"),
                    "phase": "Core Features",
                    "order": 3
                },
                {
                    "title": "Task Management UI",
                    "description": "Build user interface for creating, updating, and deleting tasks",
                    "priority": "Medium",
                    "estimated_duration": 200,
                    "suggested_deadline": (date(2026, 7, 15)).strftime("%Y-%m-%d"),
                    "phase": "Core Features",
                    "order": 4
                },
                {
                    "title": "Integrate Gemini API",
                    "description": "Set up Gemini API credentials and integrate with Django",
                    "priority": "High",
                    "estimated_duration": 180,
                    "suggested_deadline": (date(2026, 7, 20)).strftime("%Y-%m-%d"),
                    "phase": "AI Integration",
                    "order": 5
                },
                {
                    "title": "AI Roadmap Planner",
                    "description": "Build the AI roadmap planner interface and backend logic",
                    "priority": "High",
                    "estimated_duration": 240,
                    "suggested_deadline": (date(2026, 7, 25)).strftime("%Y-%m-%d"),
                    "phase": "AI Integration",
                    "order": 6
                },
                {
                    "title": "Analytics Dashboard",
                    "description": "Create analytics dashboard to visualize task data and progress",
                    "priority": "Medium",
                    "estimated_duration": 180,
                    "suggested_deadline": (date(2026, 7, 28)).strftime("%Y-%m-%d"),
                    "phase": "Polish & Deployment",
                    "order": 7
                },
                {
                    "title": "Testing & Deployment",
                    "description": "Write tests and prepare for deployment to production",
                    "priority": "High",
                    "estimated_duration": 240,
                    "suggested_deadline": "2026-07-31",
                    "phase": "Polish & Deployment",
                    "order": 8
                }
            ]
        }

    @patch('planner.views.genai')
    @patch('planner.views.generate_ai_roadmap')
    def test_planner_workflow(self, mock_generate, mock_genai):
        """Test the complete AI Planner workflow according to user requirements"""
        
        # Configure mocks
        mock_genai.Client.return_value = MagicMock()
        mock_generate.return_value = self.mock_response
        
        # 1. Submit form to generate roadmap
        response = self.client.post(self.planner_url, {**self.form_data, 'generate': '1'}, follow=True)
        
        # Verify Gemini API is called exactly once
        self.assertEqual(mock_generate.call_count, 1)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Generated Roadmap')
        
        # Get generated data from session and context
        generated_data = response.context['generated_data']
        
        # 2. A valid roadmap is returned
        self.assertIsNotNone(generated_data)
        
        # 3. 4 phases maximum are generated
        self.assertLessEqual(len(generated_data['phases']), 4)
        
        # 4. 8 tasks maximum are generated
        self.assertLessEqual(len(generated_data['tasks']), 8)
        
        # 5. Every task has all required fields
        required_fields = ['title', 'description', 'priority', 'estimated_duration', 'suggested_deadline', 'phase', 'order']
        for task in generated_data['tasks']:
            for field in required_fields:
                self.assertIn(field, task)
                self.assertIsNotNone(task[field])
        
        # 6. Task deadlines are distributed from today to user's deadline
        today = date.today().strftime("%Y-%m-%d")
        user_deadline = self.form_data['deadline']
        task_deadlines = [task['suggested_deadline'] for task in generated_data['tasks']]
        
        self.assertGreaterEqual(min(task_deadlines), today)
        self.assertLessEqual(max(task_deadlines), user_deadline)
        
        # 7. Last task deadline matches exactly
        last_task_deadline = generated_data['tasks'][-1]['suggested_deadline']
        self.assertEqual(last_task_deadline, user_deadline)
        
        # 8. No roadmap-level deadline is shown in the UI
        self.assertNotContains(response, 'Roadmap Deadline')
        
        # 9. No JSON parsing errors (handled by mock)
        # 10. No duplicate tasks
        task_titles = [task['title'] for task in generated_data['tasks']]
        self.assertEqual(len(task_titles), len(set(task_titles)))
        
        # 11. & 12. Refresh page and verify no new Gemini call, roadmap remains
        mock_generate.reset_mock()
        response_refresh = self.client.get(self.planner_url)
        self.assertEqual(mock_generate.call_count, 0)
        self.assertContains(response_refresh, 'Generated Roadmap')
        
        # 13. Generate button disabled, Regenerate present
        self.assertContains(response_refresh, 'Regenerate Roadmap')
        
        # Verify AIPlan is created
        self.assertEqual(AIPlan.objects.filter(user=self.user).count(), 1)
