import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import sys
import os

# Set up import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utility.analytics.data_processor import (
    get_study_summary,
    get_learning_curve_data,
    get_task_performance_data,
    get_participant_data
)

from app.utility.analytics.visualization_helpers import (
    plot_to_base64,
    generate_task_completion_chart,
    calculate_interaction_metrics
)

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        # Create mocks for database connection
        self.conn = MagicMock()
        self.cursor = MagicMock()
        self.conn.cursor.return_value = self.cursor
        
        # Test study identifier
        self.study_id = "test_study_123"
    
    def test_get_study_summary(self):
        # Mock database responses for each query
        self.cursor.fetchone.side_effect = [
            (25,),             # participant_count
            (300.5,),          # avg_completion_time
            (85.2,),           # success_rate
            (5,),              # task_count
            (3.7,)             # avg_error_count
        ]
        
        # Test with fixed random values
        with patch('numpy.random.uniform', return_value=5.0):
            result = get_study_summary(self.conn, self.study_id)
        
        # Verify correct number of queries were executed
        self.assertEqual(self.cursor.execute.call_count, 5)
        
        # Verify result structure and values
        self.assertIsInstance(result, dict)
        self.assertEqual(result["participantCount"], 25)
        self.assertEqual(result["avgCompletionTime"], 300.5)
        self.assertEqual(result["successRate"], 85.2)
        self.assertEqual(result["taskCount"], 5)
        self.assertEqual(result["avgErrorCount"], 3.7)
        
        # Verify metrics array format
        self.assertIn("metrics", result)
        self.assertEqual(len(result["metrics"]), 4)
        
        # Check that each metric has all required fields
        for metric in result["metrics"]:
            self.assertIn("title", metric)
            self.assertIn("value", metric)
            self.assertIn("icon", metric)
            self.assertIn("color", metric)
    
    def test_get_learning_curve_data(self):
        # Mock response for tasks and attempt data
        self.cursor.fetchall.side_effect = [
            [(1, "Task 1"), (2, "Task 2")],       # List of tasks
            [(1, 120.5, 2.5), (2, 95.2, 1.8)],    # Task 1 attempts
            [(1, 150.3, 3.2), (2, 110.5, 2.1)]    # Task 2 attempts
        ]
        
        # Get learning curve data
        result = get_learning_curve_data(self.conn, self.study_id)
        
        # Verify database queries
        self.assertEqual(self.cursor.execute.call_count, 3)
        
        # Check result format
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 4)  # 2 tasks × 2 attempts
        
        # Verify data for first attempt
        self.assertEqual(result[0]["taskId"], 1)
        self.assertEqual(result[0]["taskName"], "Task 1")
        self.assertEqual(result[0]["attempt"], 1)
        self.assertEqual(result[0]["completionTime"], 120.5)
        self.assertEqual(result[0]["errorCount"], 2.5)
    
    def test_get_task_performance_data(self):
        # Mock response for tasks and performance metrics
        self.cursor.fetchall.side_effect = [
            [(1, "Task 1"), (2, "Task 2")],    # List of tasks
            [(100.5, 85.0, 2.5)],              # Task 1 performance
            [(120.3, 75.5, 3.2)]               # Task 2 performance
        ]
        
        # Get task performance data
        result = get_task_performance_data(self.conn, self.study_id)
        
        # Verify database queries
        self.assertEqual(self.cursor.execute.call_count, 3)
        
        # Check result format
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)  # 2 tasks
        
        # Verify data for first task
        task1 = result[0]
        self.assertEqual(task1["taskId"], 1)
        self.assertEqual(task1["taskName"], "Task 1")
        self.assertEqual(task1["avgCompletionTime"], 100.5)
        self.assertEqual(task1["successRate"], 85.0)
        self.assertIsInstance(task1["errorRate"], float)
    
    def test_get_participant_data(self):
        # Mock response for participants and their data
        self.cursor.fetchall.side_effect = [
            [("P001",), ("P002",)],                      # List of participants
            [(1, 350.2, "completed"), (2, 420.5, "failed")],  # P001 sessions
            [(15,)],                                     # P001 errors
            [(1, 280.5, "completed")],                   # P002 sessions
            [(8,)]                                       # P002 errors
        ]
        
        # Get participant data
        result = get_participant_data(self.conn, self.study_id)
        
        # Verify database queries
        self.assertEqual(self.cursor.execute.call_count, 5)
        
        # Check result format
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)  # 2 participants
        
        # Verify first participant's data
        p1 = result[0]
        self.assertEqual(p1["participantId"], "P001")
        self.assertEqual(p1["sessionCount"], 2)
        self.assertEqual(p1["completionTime"], 350.2 + 420.5)
        self.assertEqual(p1["successRate"], 50.0)  # 1 of 2 sessions completed
        self.assertEqual(p1["errorCount"], 15)

class TestVisualizationHelpers(unittest.TestCase):
    @patch('matplotlib.pyplot.savefig')
    def test_plot_to_base64(self, mock_savefig):
        # Test conversion of plot to base64 image
        def mock_plot_function():
            pass
        
        # Convert plot to base64
        with patch('io.BytesIO') as mock_bytesio:
            mock_bytesio.return_value.read.return_value = b'test_image_data'
            result = plot_to_base64(mock_plot_function)
        
        # Verify result type
        self.assertIsInstance(result, str)
    
    @patch('app.utility.analytics.visualization_helpers.plot_to_base64')
    def test_generate_task_completion_chart(self, mock_plot_to_base64):
        # Test chart generation with sample data
        task_data = [
            {
                "taskId": 1,
                "taskName": "Task 1",
                "successRate": 85.0
            },
            {
                "taskId": 2,
                "taskName": "Task 2",
                "successRate": 75.5
            }
        ]
        
        # Mock the base64 conversion
        mock_plot_to_base64.return_value = "base64_chart_data"
        
        # Generate chart
        result = generate_task_completion_chart(task_data)
        
        # Verify result and function call
        self.assertEqual(result, "base64_chart_data")
        self.assertEqual(mock_plot_to_base64.call_count, 1)
    
    def test_calculate_interaction_metrics(self):
        # Test calculation of interaction metrics
        interaction_data = [
            {"type": "mouse_click"},
            {"type": "mouse_click"},
            {"type": "key_press"},
            {"type": "key_press"},
            {"type": "key_press"},
            {"type": "mouse_move"},
            {"type": "mouse_move"},
            {"type": "mouse_move"},
            {"type": "mouse_move"},
            {"type": "scroll"},
            {"type": "scroll"}
        ]
        
        # Calculate metrics for a 60-second duration
        result = calculate_interaction_metrics(interaction_data, 60)
        
        # Verify structure and values
        self.assertIsInstance(result, dict)
        self.assertIn("clicks", result)
        self.assertIn("keyPresses", result)
        self.assertIn("mouseMoves", result)
        self.assertIn("scrolls", result)
        
        # Check per-minute rates
        self.assertEqual(result["clicks"], 2)      # 2 clicks in 60 seconds
        self.assertEqual(result["keyPresses"], 3)  # 3 key presses in 60 seconds
        self.assertEqual(result["mouseMoves"], 4)  # 4 mouse moves in 60 seconds
        self.assertEqual(result["scrolls"], 2)     # 2 scrolls in 60 seconds
    
    def test_calculate_interaction_metrics_empty_data(self):
        # Test with no interaction data
        result = calculate_interaction_metrics([], 60)
        
        # Should return all zeros
        self.assertEqual(result["clicks"], 0)
        self.assertEqual(result["keyPresses"], 0)
        self.assertEqual(result["mouseMoves"], 0)
        self.assertEqual(result["scrolls"], 0)
    
    def test_calculate_interaction_metrics_zero_duration(self):
        # Test handling of zero duration (avoid division by zero)
        result = calculate_interaction_metrics([{"type": "mouse_click"}], 0)
        
        # Should handle division by zero gracefully
        self.assertEqual(result["clicks"], 0)
        self.assertEqual(result["keyPresses"], 0)
        self.assertEqual(result["mouseMoves"], 0)
        self.assertEqual(result["scrolls"], 0)

if __name__ == '__main__':
    unittest.main()