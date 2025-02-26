import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
from io import BytesIO

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.routes.analytics import analytics_bp
from flask import Flask

class TestAnalyticsRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(analytics_bp)
        self.client = self.app.test_client()
        
        # Mock database connection
        self.db_patcher = patch('app.routes.analytics.get_db_connection')
        self.mock_db = self.db_patcher.start()
        self.mock_conn = MagicMock()
        self.mock_db.return_value = self.mock_conn
        
    def tearDown(self):
        self.db_patcher.stop()
    
    @patch('app.routes.analytics.get_study_summary')
    def test_get_study_summary(self, mock_get_summary):
        # Mock data
        mock_summary = {
            "participantCount": 25,
            "avgCompletionTime": 342.5,
            "successRate": 87.2,
            "metrics": []
        }
        mock_get_summary.return_value = mock_summary
        
        # Make request
        response = self.client.get('/api/analytics/123/summary')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), mock_summary)
        mock_get_summary.assert_called_once_with(self.mock_conn, '123')
        self.mock_conn.close.assert_called_once()
    
    @patch('app.routes.analytics.get_learning_curve_data')
    def test_get_learning_curve(self, mock_get_learning_curve):
        # Mock data
        mock_data = [
            {"taskId": 1, "taskName": "Task 1", "attempt": 1, "completionTime": 120.5, "errorCount": 2.5},
            {"taskId": 1, "taskName": "Task 1", "attempt": 2, "completionTime": 95.2, "errorCount": 1.8}
        ]
        mock_get_learning_curve.return_value = mock_data
        
        # Make request
        response = self.client.get('/api/analytics/123/learning-curve')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), mock_data)
        mock_get_learning_curve.assert_called_once_with(self.mock_conn, '123')
        self.mock_conn.close.assert_called_once()
    
    @patch('app.routes.analytics.get_task_performance_data')
    def test_get_task_performance(self, mock_get_task_performance):
        # Mock data
        mock_data = [
            {
                "taskId": 1,
                "taskName": "Task 1",
                "avgCompletionTime": 120.5,
                "successRate": 85.0,
                "errorRate": 2.3,
                "avgErrors": 3.1
            }
        ]
        mock_get_task_performance.return_value = mock_data
        
        # Make request
        response = self.client.get('/api/analytics/123/task-performance')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), mock_data)
        mock_get_task_performance.assert_called_once_with(self.mock_conn, '123')
        self.mock_conn.close.assert_called_once()
    
    @patch('app.routes.analytics.get_participant_data')
    def test_get_participants(self, mock_get_participant_data):
        # Mock data
        mock_data = [
            {
                "participantId": "P001",
                "sessionCount": 2,
                "completionTime": 450.2,
                "successRate": 75.0,
                "errorCount": 12
            }
        ]
        mock_get_participant_data.return_value = mock_data
        
        # Make request
        response = self.client.get('/api/analytics/123/participants')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), mock_data)
        mock_get_participant_data.assert_called_once_with(self.mock_conn, '123')
        self.mock_conn.close.assert_called_once()
    
    @patch('app.routes.analytics.get_study_summary')
    @patch('app.routes.analytics.get_task_performance_data')
    @patch('app.routes.analytics.get_participant_data')
    def test_export_data_csv(self, mock_get_participant_data, mock_get_task_performance, mock_get_summary):
        # Mock data
        mock_summary = {
            "participantCount": 25,
            "avgCompletionTime": 342.5,
            "successRate": 87.2
        }
        mock_task_performance = [
            {
                "taskId": 1,
                "taskName": "Task 1",
                "avgCompletionTime": 120.5,
                "successRate": 85.0,
                "errorRate": 2.3
            }
        ]
        mock_participants = [
            {
                "participantId": "P001",
                "sessionCount": 2,
                "completionTime": 450.2,
                "successRate": 75.0,
                "errorCount": 12
            }
        ]
        
        mock_get_summary.return_value = mock_summary
        mock_get_task_performance.return_value = mock_task_performance
        mock_get_participant_data.return_value = mock_participants
        
        # Make request
        response = self.client.get('/api/analytics/123/export?format=csv')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/csv; charset=utf-8')
        self.assertTrue('attachment' in response.headers['Content-Disposition'])
        
        # Check that CSV data contains our mock data (basic check)
        csv_data = response.data.decode('utf-8')
        self.assertIn('Study Summary', csv_data)
        self.assertIn('Task Performance', csv_data)
        self.assertIn('Participant Data', csv_data)
        self.assertIn('Task 1', csv_data)
        self.assertIn('P001', csv_data)
    
    @patch('app.routes.analytics.get_study_summary')
    @patch('app.routes.analytics.get_task_performance_data')
    @patch('app.routes.analytics.get_participant_data')
    def test_export_data_json(self, mock_get_participant_data, mock_get_task_performance, mock_get_summary):
        # Mock data
        mock_summary = {
            "participantCount": 25,
            "avgCompletionTime": 342.5,
            "successRate": 87.2
        }
        mock_task_performance = [
            {
                "taskId": 1,
                "taskName": "Task 1",
                "avgCompletionTime": 120.5,
                "successRate": 85.0,
                "errorRate": 2.3
            }
        ]
        mock_participants = [
            {
                "participantId": "P001",
                "sessionCount": 2,
                "completionTime": 450.2,
                "successRate": 75.0,
                "errorCount": 12
            }
        ]
        
        mock_get_summary.return_value = mock_summary
        mock_get_task_performance.return_value = mock_task_performance
        mock_get_participant_data.return_value = mock_participants
        
        # Make request
        response = self.client.get('/api/analytics/123/export?format=json')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertTrue('attachment' in response.headers['Content-Disposition'])
        
        # Check that JSON data contains our mock data
        json_data = json.loads(response.data)
        self.assertEqual(json_data['summary'], mock_summary)
        self.assertEqual(json_data['taskPerformance'], mock_task_performance)
        self.assertEqual(json_data['participants'], mock_participants)
    
    def test_export_data_invalid_format(self):
        # Make request with invalid format
        response = self.client.get('/api/analytics/123/export?format=xml')
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('Unsupported export format', response_data['error'])
    
    @patch('app.routes.analytics.get_study_summary')
    def test_error_handling(self, mock_get_summary):
        # Mock an exception
        mock_get_summary.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.get('/api/analytics/123/summary')
        
        # Assertions
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], "Database error")

if __name__ == '__main__':
    unittest.main()