import sqlite3
import pandas as pd
from local_config import DB_CONFIG, USE_SQLITE, DB_PATH

def get_connection():
    """Get a database connection"""
    if USE_SQLITE:
        # Use SQLite for local development
        return sqlite3.connect(DB_CONFIG['SQLITE']['path'])
    else:
        # This would be your original code to connect to MySQL
        # For now, fall back to SQLite
        return sqlite3.connect(DB_CONFIG['SQLITE']['path'])

def query_db(query, params=(), one=False):
    """Query the database and return results as a list of dictionaries"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row  # This enables dictionary-like access to rows
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    rv = cursor.fetchall()
    conn.close()
    
    # Convert rows to dictionaries
    result = [dict(row) for row in rv]
    return (result[0] if result else None) if one else result

def query_df(query, params=()):
    """Query the database and return results as a pandas DataFrame"""
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute_db(query, params=()):
    """Execute a database query without returning results (for INSERT, UPDATE, DELETE)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return cursor.rowcount  # Return the number of affected rows

# Specific query functions for the application
def get_studies():
    """Get all studies"""
    return query_db("SELECT * FROM studies")

def get_participants(study_id=None):
    """Get all participants, optionally filtered by study_id"""
    if study_id:
        return query_db("SELECT * FROM participants WHERE study_id = ?", (study_id,))
    else:
        return query_db("SELECT * FROM participants")

def get_tasks():
    """Get all tasks"""
    return query_db("SELECT * FROM tasks")

def get_performance_data(participant_id=None, task_id=None):
    """Get performance data, optionally filtered by participant_id or task_id"""
    query = "SELECT * FROM performance"
    params = []
    
    where_clauses = []
    if participant_id:
        where_clauses.append("participant_id = ?")
        params.append(participant_id)
    if task_id:
        where_clauses.append("task_id = ?")
        params.append(task_id)
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    return query_db(query, tuple(params))

def get_summary_stats():
    """Get summary statistics for the dashboard"""
    stats = {}
    
    # Get participant count
    stats['participant_count'] = query_db("SELECT COUNT(*) as count FROM participants", one=True)['count']
    
    # Get task count
    stats['task_count'] = query_db("SELECT COUNT(*) as count FROM tasks", one=True)['count']
    
    # Get average completion time
    stats['avg_completion_time'] = query_db(
        "SELECT AVG(completion_time) as avg_time FROM performance", one=True)['avg_time']
    
    # Get success rate
    stats['success_rate'] = query_db(
        "SELECT AVG(success) * 100 as rate FROM performance", one=True)['rate']
    
    # Get total interactions
    stats['total_interactions'] = query_db(
        "SELECT COUNT(*) as count FROM interactions", one=True)['count']
    
    # Get error rate
    stats['error_rate'] = query_db(
        "SELECT SUM(error_count) / COUNT(*) as rate FROM performance", one=True)['rate']
    
    return stats

def get_learning_curve_data():
    """Get learning curve data for visualization"""
    return query_db("""
        SELECT 
            trial, 
            AVG(completion_time) as avg_completion_time,
            AVG(error_count) as avg_error_count,
            AVG(success) * 100 as success_rate
        FROM performance
        GROUP BY trial
        ORDER BY trial
    """)

def get_task_comparison_data():
    """Get task comparison data for visualization"""
    return query_db("""
        SELECT 
            t.id as task_id,
            t.name as task_name,
            AVG(p.completion_time) as avg_completion_time,
            AVG(p.error_count) as avg_error_count,
            AVG(p.success) * 100 as success_rate
        FROM performance p
        JOIN tasks t ON p.task_id = t.id
        GROUP BY t.id, t.name
        ORDER BY t.id
    """)