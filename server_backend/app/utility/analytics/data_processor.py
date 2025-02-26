import numpy as np
from datetime import datetime
from collections import defaultdict

def get_study_summary(conn, study_id):
    """Get dashboard summary metrics for a study"""
    # Get total unique participants
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(DISTINCT participant_id) FROM sessions WHERE study_id = ?",
        (study_id,)
    )
    participant_count = cursor.fetchone()[0]
    
    # Calculate average time to complete sessions
    cursor.execute(
        """
        SELECT AVG(end_time - start_time) 
        FROM sessions 
        WHERE study_id = ? AND status = 'completed'
        """,
        (study_id,)
    )
    avg_completion_time = cursor.fetchone()[0] or 0
    
    # Calculate percentage of successfully completed sessions
    cursor.execute(
        """
        SELECT 
            COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*) 
        FROM sessions 
        WHERE study_id = ?
        """,
        (study_id,)
    )
    success_rate = cursor.fetchone()[0] or 0
    
    # Count how many tasks are in the study
    cursor.execute(
        "SELECT COUNT(DISTINCT task_id) FROM tasks WHERE study_id = ?",
        (study_id,)
    )
    task_count = cursor.fetchone()[0]
    
    # Get average number of errors per task attempt
    cursor.execute(
        """
        SELECT AVG(error_count) 
        FROM task_results 
        WHERE session_id IN (SELECT id FROM sessions WHERE study_id = ?)
        """,
        (study_id,)
    )
    avg_error_count = cursor.fetchone()[0] or 0
    
    # Generate trend indicators (random for demo purposes)
    completion_time_change = round(np.random.uniform(-15, 15), 1)
    success_rate_change = round(np.random.uniform(-10, 10), 1)
    error_count_change = round(np.random.uniform(-20, 20), 1)
    
    # Format data for dashboard display
    return {
        "participantCount": participant_count,
        "avgCompletionTime": round(avg_completion_time, 2),
        "successRate": round(success_rate, 2),
        "taskCount": task_count,
        "avgErrorCount": round(avg_error_count, 2),
        "metrics": [
            {
                "title": "Participants",
                "value": participant_count,
                "icon": "mdi-account-group",
                "color": "primary"
            },
            {
                "title": "Avg Completion Time",
                "value": f"{round(avg_completion_time, 2)}s",
                "change": completion_time_change,
                "icon": "mdi-clock-outline",
                "color": "info"
            },
            {
                "title": "Success Rate",
                "value": f"{round(success_rate, 2)}%",
                "change": success_rate_change,
                "icon": "mdi-check-circle-outline",
                "color": "success" 
            },
            {
                "title": "Avg Error Count",
                "value": round(avg_error_count, 2),
                "change": error_count_change,
                "icon": "mdi-alert-circle-outline",
                "color": "error"
            }
        ]
    }

def get_learning_curve_data(conn, study_id):
    """Get data showing how performance improves with practice"""
    cursor = conn.cursor()
    
    # Get list of tasks in this study
    cursor.execute(
        "SELECT id, name FROM tasks WHERE study_id = ?",
        (study_id,)
    )
    tasks = cursor.fetchall()
    
    result = []
    
    for task_id, task_name in tasks:
        # For each task, get metrics by attempt number
        cursor.execute(
            """
            SELECT 
                tr.attempt_number,
                AVG(tr.completion_time) as avg_time,
                AVG(tr.error_count) as avg_errors
            FROM task_results tr
            JOIN sessions s ON tr.session_id = s.id
            WHERE 
                s.study_id = ? AND 
                tr.task_id = ?
            GROUP BY tr.attempt_number
            ORDER BY tr.attempt_number
            """,
            (study_id, task_id)
        )
        
        task_data = cursor.fetchall()
        
        # Format the data for the learning curve chart
        for attempt, avg_time, avg_errors in task_data:
            result.append({
                "taskId": task_id,
                "taskName": task_name,
                "attempt": attempt,
                "completionTime": round(avg_time, 2),
                "errorCount": round(avg_errors, 2)
            })
    
    return result

def get_task_performance_data(conn, study_id):
    """Get comparative performance metrics across different tasks"""
    cursor = conn.cursor()
    
    # Get list of tasks in this study
    cursor.execute(
        "SELECT id, name FROM tasks WHERE study_id = ?",
        (study_id,)
    )
    tasks = cursor.fetchall()
    
    result = []
    
    for task_id, task_name in tasks:
        # For each task, calculate performance metrics
        cursor.execute(
            """
            SELECT 
                AVG(tr.completion_time) as avg_time,
                COUNT(CASE WHEN tr.status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as success_rate,
                AVG(tr.error_count) as avg_errors
            FROM task_results tr
            JOIN sessions s ON tr.session_id = s.id
            WHERE 
                s.study_id = ? AND 
                tr.task_id = ?
            """,
            (study_id, task_id)
        )
        
        avg_time, success_rate, avg_errors = cursor.fetchone()
        
        # Calculate errors per minute as a normalized metric
        error_rate = avg_errors / (avg_time / 60) if avg_time > 0 else 0
        
        # Format task data for the comparison chart
        result.append({
            "taskId": task_id,
            "taskName": task_name,
            "avgCompletionTime": round(avg_time or 0, 2),
            "successRate": round(success_rate or 0, 2),
            "errorRate": round(error_rate, 2),
            "avgErrors": round(avg_errors or 0, 2)
        })
    
    return result

def get_participant_data(conn, study_id):
    """Get performance data for individual participants"""
    cursor = conn.cursor()
    
    # Get list of participants in this study
    cursor.execute(
        """
        SELECT DISTINCT participant_id 
        FROM sessions 
        WHERE study_id = ?
        """,
        (study_id,)
    )
    
    participants = [row[0] for row in cursor.fetchall()]
    result = []
    
    for participant_id in participants:
        # Get all sessions for this participant
        cursor.execute(
            """
            SELECT 
                id,
                end_time - start_time as duration,
                status
            FROM sessions 
            WHERE 
                study_id = ? AND 
                participant_id = ?
            """,
            (study_id, participant_id)
        )
        
        sessions = cursor.fetchall()
        
        # Calculate overall metrics for this participant
        session_count = len(sessions)
        completion_time = sum(duration for _, duration, _ in sessions if duration)
        completed_sessions = sum(1 for _, _, status in sessions if status == 'completed')
        success_rate = (completed_sessions / session_count * 100) if session_count > 0 else 0
        
        # Get total error count across all tasks
        cursor.execute(
            """
            SELECT 
                SUM(error_count) as total_errors
            FROM task_results tr
            JOIN sessions s ON tr.session_id = s.id
            WHERE 
                s.study_id = ? AND 
                s.participant_id = ?
            """,
            (study_id, participant_id)
        )
        
        total_errors = cursor.fetchone()[0] or 0
        
        # Format participant data for the table
        result.append({
            "participantId": participant_id,
            "sessionCount": session_count,
            "completionTime": round(completion_time, 2),
            "successRate": round(success_rate, 2),
            "errorCount": total_errors
        })
    
    return result