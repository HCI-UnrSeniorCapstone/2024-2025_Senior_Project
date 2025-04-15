#!/usr/bin/env python3
"""
Test analytics queries to verify that we don't need the views from fix_analytics.py
"""
import os
import sys
import mysql.connector
from datetime import datetime

def get_db_connection():
    """Create direct database connection for testing"""
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', 'flatRabbit86^')
    db = os.getenv('MYSQL_DB', 'DEVELOP_fulcrum')
    
    print(f"Connecting to database {db} at {host} with user {user}...")
    
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            passwd=password,
            database=db
        )
        print("Database connection successful!")
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def test_analytics_queries():
    """Test the analytics queries that were dependent on views"""
    conn = get_db_connection()
    
    if not conn:
        print("Cannot proceed without database connection")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    # Test each query type that the analytics module depends on
    study_id = 1  # Use a test study ID
    
    queries = [
        {
            "description": "Get study participants count",
            "query": """
                SELECT COUNT(DISTINCT participant_id) as count 
                FROM participant_session 
                WHERE study_id = %s
            """,
            "params": (study_id,)
        },
        {
            "description": "Get study tasks count",
            "query": """
                SELECT COUNT(*) as count
                FROM task
                WHERE study_id = %s
            """,
            "params": (study_id,)
        },
        {
            "description": "Get average completion time",
            "query": """
                SELECT AVG(TIMESTAMPDIFF(SECOND, created_at, ended_at)) as avg_time
                FROM participant_session 
                WHERE study_id = %s AND ended_at IS NOT NULL
            """,
            "params": (study_id,)
        },
        {
            "description": "Get session completion rate",
            "query": """
                SELECT 
                    COUNT(CASE WHEN ended_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) as rate
                FROM participant_session 
                WHERE study_id = %s
            """,
            "params": (study_id,)
        },
        {
            "description": "Get trial data",
            "query": """
                SELECT 
                    t.trial_id,
                    ROW_NUMBER() OVER (PARTITION BY ps.participant_id, t.task_id ORDER BY t.started_at) as attempt_number,
                    TIMESTAMPDIFF(SECOND, t.started_at, t.ended_at) as completion_time,
                    COUNT(sdi.session_data_instance_id) as error_count,
                    CASE WHEN t.ended_at IS NOT NULL THEN 'completed' ELSE 'in_progress' END as status
                FROM trial t
                JOIN participant_session ps ON t.participant_session_id = ps.participant_session_id
                LEFT JOIN session_data_instance sdi ON t.trial_id = sdi.trial_id
                WHERE ps.study_id = %s
                GROUP BY t.trial_id, t.participant_session_id, t.task_id, ps.participant_id, t.started_at, t.ended_at
                LIMIT 5
            """,
            "params": (study_id,)
        }
    ]
    
    success = True
    
    print("\nTesting analytics queries without database views...")
    
    for query_test in queries:
        try:
            print(f"\n--- {query_test['description']} ---")
            cursor.execute(query_test["query"], query_test["params"])
            results = cursor.fetchall()
            
            if results:
                for row in results[:3]:  # Show only first 3 rows
                    print(f"  {row}")
                if len(results) > 3:
                    print(f"  ... and {len(results) - 3} more rows")
            else:
                print("  No results returned")
                
            print(f"✅ Query successful")
        except Exception as e:
            print(f"❌ Query failed: {e}")
            success = False
    
    cursor.close()
    conn.close()
    
    if success:
        print("\n✅ SUCCESS: All analytics queries work without the view definitions")
        print("The fix_analytics.py script is no longer needed")
    else:
        print("\n❌ FAILURE: Some analytics queries failed")
        print("There may still be dependencies on the views from fix_analytics.py")
    
    return success

if __name__ == "__main__":
    success = test_analytics_queries()
    sys.exit(0 if success else 1)