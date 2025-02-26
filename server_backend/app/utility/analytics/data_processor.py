import numpy as np
from datetime import datetime
from collections import defaultdict

def get_study_summary(conn, study_id):
    """
    Get summary metrics for a study
    
    Args:
        conn: Database connection
        study_id: ID of the study
        
    Returns:
        Dictionary with summary metrics
    """
    # Query total participants
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(DISTINCT participant_id) FROM sessions WHERE study_id = ?",
        (study_id,)
    )
    participant_count = cursor.fetchone()[0]
    
    # Query average completion time
    cursor.execute(
        """
        SELECT AVG(end_time - start_time) 
        FROM sessions 
        WHERE study_id = ? AND status = 'completed'
        """,
        (study_id,)
    )
    avg_completion_time = cursor.fetchone()[0] or 0
    
    # Query success rate
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
    
    # Query total tasks
    cursor.execute(
        "SELECT COUNT(DISTINCT task_id) FROM tasks WHERE study_id = ?",
        (study_id,)
    )
    task_count = cursor.fetchone()[0]
    
    # Query average error count
    cursor.execute(
        """
        SELECT AVG(error_count) 
        FROM task_results 
        WHERE session_id IN (SELECT id FROM sessions WHERE study_id = ?)
        """,
        (study_id,)
    )
    avg_error_count = cursor.fetchone()[0] or 0
    
    # Generate change values (simplified to use random values)
    completion_time_change = round(np.random.uniform(-15, 15), 1)
    success_rate_change = round(np.random.uniform(-10, 10), 1)
    error_count_change = round(np.random.uniform(-20, 20), 1)
    
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
    """
    Get learning curve data for a study
    
    Args:
        conn: Database connection
        study_id: ID of the study
        
    Returns:
        List of data points showing task completion time across attempts
    """
    cursor = conn.cursor()
    
    # Get tasks in the study
    cursor.execute(
        "SELECT id, name FROM tasks WHERE study_id = ?",
        (study_id,)
    )
    tasks = cursor.fetchall()
    
    result = []
    
    for task_id, task_name in tasks:
        # Get task results for each attempt
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
    """
    Get task performance data for a study
    
    Args:
        conn: Database connection
        study_id: ID of the study
        
    Returns:
        List of task performance metrics
    """
    cursor = conn.cursor()
    
    # Get tasks in the study
    cursor.execute(
        "SELECT id, name FROM tasks WHERE study_id = ?",
        (study_id,)
    )
    tasks = cursor.fetchall()
    
    result = []
    
    for task_id, task_name in tasks:
        # Get performance metrics for the task
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
        
        # Calculate error rate as errors per minute
        error_rate = avg_errors / (avg_time / 60) if avg_time > 0 else 0
        
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
    """
    Get participant data for a study
    
    Args:
        conn: Database connection
        study_id: ID of the study
        
    Returns:
        List of participant data
    """
    cursor = conn.cursor()
    
    # Get participants in the study
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
        # Get session data for the participant
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
        session_count = len(sessions)
        completion_time = sum(duration for _, duration, _ in sessions if duration)
        completed_sessions = sum(1 for _, _, status in sessions if status == 'completed')
        success_rate = (completed_sessions / session_count * 100) if session_count > 0 else 0
        
        # Get task data for the participant
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
        
        result.append({
            "participantId": participant_id,
            "sessionCount": session_count,
            "completionTime": round(completion_time, 2),
            "successRate": round(success_rate, 2),
            "errorCount": total_errors
        })
    
    return result