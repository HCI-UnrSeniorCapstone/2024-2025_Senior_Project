from flask import Flask, jsonify, request
from flask_cors import CORS

# Import local configuration and database modules
import local_db
from local_config import DEBUG, PORT, CORS_ALLOWED_ORIGINS, DB_CONFIG

# Set up Flask app with CORS for API routes
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": CORS_ALLOWED_ORIGINS}})

# Routes for analytics data
@app.route('/api/analytics/summary', methods=['GET'])
def get_summary_stats(study_id=None):
    """Get summary metrics for dashboard cards"""
    import logging
    import traceback
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Get study_id from URL param if not passed directly
    if study_id is None:
        study_id = request.args.get('study_id', type=int)
    
    try:
        # SQL query to calculate all summary metrics at once
        query = """
        WITH study_analysis AS (
            SELECT 
                s.study_id,
                
                -- Participant Count
                COUNT(DISTINCT s.participant_id) as total_participants,
                
                -- Completed Sessions Calculation
                COUNT(CASE WHEN s.status = 'completed' THEN 1 END) as completed_sessions,
                
                -- Completion Time for Completed Sessions
                AVG(
                    CASE 
                        WHEN s.status = 'completed' 
                             AND s.start_time IS NOT NULL 
                             AND s.end_time IS NOT NULL
                        THEN s.end_time - s.start_time 
                        ELSE NULL 
                    END
                ) as avg_completion_time,
                
                -- Success Rate Calculation
                (
                    COUNT(CASE WHEN s.status = 'completed' THEN 1 END) * 100.0 / 
                    NULLIF(COUNT(*), 0)
                ) as success_rate,
                
                -- Tasks and Errors
                COUNT(DISTINCT t.id) as total_tasks,
                AVG(tr.error_count) as avg_error_count,
                
                -- Total Sessions
                COUNT(*) as total_sessions
            FROM studies st
            LEFT JOIN sessions s ON st.id = s.study_id
            LEFT JOIN tasks t ON st.id = t.study_id
            LEFT JOIN task_results tr ON s.id = tr.session_id
            WHERE st.id = %s
            GROUP BY st.id
        )
        SELECT 
            COALESCE(total_participants, 0) as participant_count,
            COALESCE(avg_completion_time, 0) as avg_completion_time,
            COALESCE(success_rate, 0) as success_rate,
            COALESCE(total_tasks, 0) as task_count,
            COALESCE(avg_error_count, 0) as avg_error_count,
            total_sessions,
            completed_sessions
        FROM study_analysis
        """
        
        # Run query and get results
        stats = local_db.execute_query(query, (study_id,), fetch_one=True)
        app.logger.info(f"Raw stats for study {study_id}: {stats}")
        
        # Convert all values to float to avoid type issues
        stats = {
            k: float(v) if v is not None else 0.0 
            for k, v in stats.items()
        }
        
        # Format data for the dashboard cards
        response = {
            "participantCount": round(stats['participant_count'], 2),
            "avgCompletionTime": round(stats['avg_completion_time'], 2),
            "successRate": round(stats['success_rate'], 2),
            "taskCount": round(stats['task_count'], 2),
            "avgErrorCount": round(stats['avg_error_count'], 2),
            "metrics": [
                {
                    "title": "Participants",
                    "value": round(stats['participant_count'], 2),
                    "icon": "mdi-account-group",
                    "color": "primary",
                    "change": 5.0
                },
                {
                    "title": "Avg Completion Time",
                    "value": f"{round(stats['avg_completion_time'], 2)}s",
                    "change": 5.0,
                    "icon": "mdi-clock-outline",
                    "color": "info"
                },
                {
                    "title": "Success Rate",
                    "value": f"{round(stats['success_rate'], 2)}%",
                    "change": 2.5,
                    "icon": "mdi-check-circle-outline",
                    "color": "success" 
                },
                {
                    "title": "Avg Error Count",
                    "value": round(stats['avg_error_count'], 2),
                    "change": -3.2,
                    "icon": "mdi-alert-circle-outline",
                    "color": "error"
                }
            ],
            "_debug": {
                "totalSessions": stats.get('total_sessions', 0),
                "completedSessions": stats.get('completed_sessions', 0)
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        # Log the full error with traceback
        app.logger.error(f"Unexpected error in summary stats for study {study_id}: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "error": "Unexpected server error",
            "details": str(e)
        }), 500

@app.route('/api/analytics/learning-curve', methods=['GET'])
def get_learning_curve():
    """Get data for the learning curve chart"""
    study_id = request.args.get('study_id', type=int)
    
    try:
        # Get attempts, completion time and errors by task
        data = local_db.execute_query(
            """
            SELECT 
                t.id as task_id,
                t.name as task_name,
                tr.attempt_number as attempt,
                AVG(tr.completion_time) as completion_time,
                AVG(tr.error_count) as error_count
            FROM task_results tr
            JOIN tasks t ON tr.task_id = t.id
            JOIN sessions s ON tr.session_id = s.id
            WHERE s.study_id = %s
            GROUP BY t.id, t.name, tr.attempt_number
            ORDER BY t.id, tr.attempt_number
            """,
            (study_id,)
        )
        
        # Format data for the chart component
        formatted_data = []
        for row in data:
            formatted_data.append({
                "taskId": row['task_id'],
                "taskName": row['task_name'],
                "attempt": row['attempt'],
                "completionTime": round(row['completion_time'] or 0, 2),
                "errorCount": round(row['error_count'] or 0, 2)
            })
            
        return jsonify(formatted_data)
    except Exception as e:
        app.logger.error(f"Error getting learning curve data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/task-comparison', methods=['GET'])
def get_task_comparison():
    """Get data for the task performance comparison chart"""
    study_id = request.args.get('study_id', type=int)
    
    try:
        # Get task performance metrics
        data = local_db.execute_query(
            """
            SELECT 
                t.id as task_id,
                t.name as task_name,
                AVG(tr.completion_time) as avg_completion_time,
                COUNT(CASE WHEN tr.status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as success_rate,
                AVG(tr.error_count) as avg_errors
            FROM tasks t
            LEFT JOIN task_results tr ON t.id = tr.task_id
            WHERE t.study_id = %s
            GROUP BY t.id, t.name
            """,
            (study_id,)
        )
        
        # Calculate error rate (errors per minute) and format response
        formatted_data = []
        for row in data:
            avg_time_minutes = (row['avg_completion_time'] or 0) / 60
            error_rate = float(row['avg_errors'] or 0) / float(avg_time_minutes) if avg_time_minutes > 0 else 0
            
            formatted_data.append({
                "taskId": row['task_id'],
                "taskName": row['task_name'],
                "avgCompletionTime": round(row['avg_completion_time'] or 0, 2),
                "successRate": round(row['success_rate'] or 0, 2),
                "errorRate": round(error_rate, 2),
                "avgErrors": round(row['avg_errors'] or 0, 2)
            })
            
        return jsonify(formatted_data)
    except Exception as e:
        app.logger.error(f"Error getting task comparison data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/<study_id>/task-performance', methods=['GET'])
def get_task_performance(study_id):
    """Get detailed task performance data for a specific study"""
    try:
        # Same query as task-comparison but with specific study_id in URL
        data = local_db.execute_query(
            """
            SELECT 
                t.id as task_id,
                t.name as task_name,
                AVG(tr.completion_time) as avg_completion_time,
                COUNT(CASE WHEN tr.status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as success_rate,
                AVG(tr.error_count) as avg_errors
            FROM tasks t
            LEFT JOIN task_results tr ON t.id = tr.task_id
            WHERE t.study_id = %s
            GROUP BY t.id, t.name
            """,
            (study_id,)
        )
        
        # Calculate and format the same way as task-comparison
        formatted_data = []
        for row in data:
            avg_time_minutes = (row['avg_completion_time'] or 0) / 60
            error_rate = float(row['avg_errors'] or 0) / float(avg_time_minutes) if avg_time_minutes > 0 else 0
            
            formatted_data.append({
                "taskId": row['task_id'],
                "taskName": row['task_name'],
                "avgCompletionTime": round(row['avg_completion_time'] or 0, 2),
                "successRate": round(row['success_rate'] or 0, 2),
                "errorRate": round(error_rate, 2),
                "avgErrors": round(row['avg_errors'] or 0, 2)
            })
            
        return jsonify(formatted_data)
    except Exception as e:
        app.logger.error(f"Error getting task performance data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/<study_id>/participants', methods=['GET'])
def get_study_participants(study_id):
    """Get participant data for the data table"""
    try:
        # Query participant metrics by study
        participants = local_db.execute_query(
            """
            SELECT 
                s.participant_id,
                COUNT(s.id) as session_count,
                SUM(s.end_time - s.start_time) as completion_time,
                COUNT(CASE WHEN s.status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as success_rate,
                SUM(tr.error_count) as error_count
            FROM sessions s
            LEFT JOIN task_results tr ON s.id = tr.session_id
            WHERE s.study_id = %s
            GROUP BY s.participant_id
            """,
            (study_id,)
        )
        
        # Format for the data table component
        formatted_data = []
        for p in participants:
            formatted_data.append({
                "participantId": p['participant_id'],
                "sessionCount": p['session_count'],
                "completionTime": round(p['completion_time'] or 0, 2),
                "successRate": round(p['success_rate'] or 0, 2),
                "errorCount": p['error_count'] or 0
            })
            
        return jsonify(formatted_data)
    except Exception as e:
        app.logger.error(f"Error getting participant data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/studies', methods=['GET'])
def get_studies():
    """Get list of available studies for the selector dropdown"""
    try:
        # Get studies with participant count and last activity timestamp
        studies = local_db.execute_query(
            """
            SELECT id, name, description, status,
                   (SELECT COUNT(DISTINCT participant_id) FROM sessions WHERE study_id = studies.id) as participant_count,
                   (SELECT MAX(start_time) FROM sessions WHERE study_id = studies.id) as last_activity
            FROM studies
            ORDER BY last_activity DESC
            """
        )
        
        # Format the data for the frontend
        for study in studies:
            if study['last_activity']:
                # Convert timestamp to ISO format
                import datetime
                timestamp = datetime.datetime.fromtimestamp(study['last_activity'])
                study['last_active'] = timestamp.isoformat()
            
            # Structure stats object for the UI
            study['stats'] = {
                'participants': study['participant_count'],
                'lastActive': study.get('last_active')
            }
            
            # Remove redundant fields
            del study['participant_count']
            if 'last_activity' in study:
                del study['last_activity']
            if 'last_active' in study:
                del study['last_active']
        
        return jsonify(studies)
    except Exception as e:
        app.logger.error(f"Error fetching studies: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/participants', methods=['GET'])
def get_participants():
    """Get list of participant IDs for a study"""
    study_id = request.args.get('study_id', type=int)
    
    try:
        # Get unique participant IDs
        participants = local_db.execute_query(
            """
            SELECT DISTINCT participant_id
            FROM sessions
            WHERE study_id = %s
            """,
            (study_id,)
        )
        
        return jsonify([p['participant_id'] for p in participants])
    except Exception as e:
        app.logger.error(f"Error getting participants: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get list of tasks for a study"""
    study_id = request.args.get('study_id', type=int)
    
    try:
        # Get basic task info
        tasks = local_db.execute_query(
            """
            SELECT id, name, description
            FROM tasks
            WHERE study_id = %s
            """,
            (study_id,)
        )
        
        return jsonify(tasks)
    except Exception as e:
        app.logger.error(f"Error getting tasks: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get performance data for a specific participant or task"""
    participant_id = request.args.get('participant_id')
    task_id = request.args.get('task_id', type=int)
    
    try:
        # Base query for participant performance
        query = """
            SELECT 
                tr.attempt_number,
                tr.completion_time,
                tr.error_count,
                tr.status
            FROM task_results tr
            JOIN sessions s ON tr.session_id = s.id
            WHERE s.participant_id = %s
        """
        params = [participant_id]
        
        # Add task filter if specified
        if task_id:
            query += " AND tr.task_id = %s"
            params.append(task_id)
            
        query += " ORDER BY tr.attempt_number"
            
        data = local_db.execute_query(query, tuple(params))
        
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error getting performance data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint for monitoring"""
    db_connected = local_db.test_connection()
    return jsonify({
        "status": "ok" if db_connected else "database error", 
        "mode": "local development",
        "database": "MySQL",
        "db_config": {
            "host": DB_CONFIG['host'],
            "database": DB_CONFIG['database'],
            "connected": db_connected
        }
    })

# Additional routes to support URL patterns for the Analytics dashboard
@app.route('/api/analytics/<int:study_id>/summary', methods=['GET'])
def get_study_summary(study_id):
    """Get summary metrics with study ID in URL path"""
    return get_summary_stats(study_id)

@app.route('/api/analytics/<int:study_id>/learning-curve', methods=['GET'])
def get_study_learning_curve(study_id):
    """Get learning curve data with study ID in URL path"""
    return get_learning_curve(study_id)

if __name__ == '__main__':
    # Verify database connection on startup
    if local_db.test_connection():
        print("Database connection successful!")
    else:
        print("Warning: Database connection failed. Please check your configuration.")
    
    # Start the Flask server
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)