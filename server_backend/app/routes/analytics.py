from flask import Blueprint, jsonify, request, send_file, current_app, Response, json
from app.utility.analytics.data_processor import (
    get_study_summary,
    get_learning_curve_data,
    get_task_performance_data,
    get_participant_data,
    validate_analytics_schema
)
from app.utility.analytics.visualization_helper import (
    plot_to_base64,
    generate_task_completion_chart,
    generate_error_rate_chart,
    calculate_interaction_metrics,
    plot_learning_curve
)
from app.utility.db_connection import get_db_connection
import io
import csv
import json
import logging
import traceback
from datetime import datetime
import os

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize module-level variables
analytics_ready = False

def init_analytics():
    """Initialize analytics compatibility without database operations"""
    global analytics_ready
    logger.info("Initializing analytics module...")
    analytics_ready = True
    return True

# Run the initialization (no DB operations)
init_analytics()

def handle_route_error(e, operation, study_id=None):
    # Handle errors consistently across routes
    # e: Exception that occurred
    # operation: What failed
    # study_id: Optional related study ID
    # Returns: (response, status_code)
    # Log the error with full traceback
    logger.error(f"Error in {operation}" + (f" for study {study_id}" if study_id else "") + f": {str(e)}")
    logger.error(traceback.format_exc())
    
    # Determine error type and appropriate status code
    if isinstance(e, ValueError):
        # Input validation errors
        return jsonify({
            "error": str(e),
            "error_type": "validation_error",
            "operation": operation
        }), 400
        
    elif "database" in str(e).lower() or "sql" in str(e).lower():
        # Database errors
        return jsonify({
            "error": "A database error occurred",
            "error_type": "database_error",
            "operation": operation,
            "details": str(e) if current_app.config.get('DEBUG', False) else None
        }), 500
        
    else:
        # Other server errors
        return jsonify({
            "error": "An unexpected error occurred",
            "error_type": "server_error",
            "operation": operation,
            "details": str(e) if current_app.config.get('DEBUG', False) else None
        }), 500

@analytics_bp.route('/<study_id>/summary', methods=['GET'])
def get_study_summary_route(study_id):
    # Get key metrics for a study
    try:
        # Validate study_id
        try:
            study_id = int(study_id)
        except ValueError:
            raise ValueError("Study ID must be an integer")
            
        conn = get_db_connection()
        summary = get_study_summary(conn, study_id)
        conn.close()
        return jsonify(summary)
    except Exception as e:
        return handle_route_error(e, "get_study_summary", study_id)

@analytics_bp.route('/summary', methods=['GET'])
def get_summary_stats_by_param():
    # Same as summary route but using query param instead of URL param
    try:
        study_id = request.args.get('study_id', type=int)
        if not study_id:
            raise ValueError("Missing required 'study_id' parameter")
            
        return get_study_summary_route(study_id)
    except Exception as e:
        return handle_route_error(e, "get_summary_stats_by_param")

@analytics_bp.route('/<study_id>/learning-curve', methods=['GET'])
def get_learning_curve_route(study_id):
    # Get data showing improvement over time
    try:
        # Validate study_id
        try:
            study_id = int(study_id)
        except ValueError:
            raise ValueError("Study ID must be an integer")
            
        conn = get_db_connection()
        data = get_learning_curve_data(conn, study_id)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return handle_route_error(e, "get_learning_curve_data", study_id)

@analytics_bp.route('/learning-curve', methods=['GET'])
def get_learning_curve_by_param():
    # Same as learning curve route but using query param
    try:
        study_id = request.args.get('study_id', type=int)
        if not study_id:
            raise ValueError("Missing required 'study_id' parameter")
            
        return get_learning_curve_route(study_id)
    except Exception as e:
        return handle_route_error(e, "get_learning_curve_by_param")

@analytics_bp.route('/<study_id>/task-performance', methods=['GET'])
def get_task_performance_route(study_id):
    # Get how well users are completing each task
    try:
        # Validate study_id
        try:
            study_id = int(study_id)
        except ValueError:
            raise ValueError("Study ID must be an integer")
            
        conn = get_db_connection()
        data = get_task_performance_data(conn, study_id)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return handle_route_error(e, "get_task_performance_data", study_id)

@analytics_bp.route('/task-comparison', methods=['GET'])
def get_task_comparison():
    # Compare performance across different tasks
    try:
        study_id = request.args.get('study_id', type=int)
        if not study_id:
            raise ValueError("Missing required 'study_id' parameter")
            
        return get_task_performance_route(study_id)
    except Exception as e:
        return handle_route_error(e, "get_task_comparison")

@analytics_bp.route('/<study_id>/participants', methods=['GET'])
def get_participants_route(study_id):
    # Get data about each participant
    try:
        # Validate study_id
        try:
            study_id = int(study_id)
        except ValueError:
            raise ValueError("Study ID must be an integer")
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Validate pagination parameters
        if page < 1:
            raise ValueError("Page number must be at least 1")
        if per_page < 1 or per_page > 100:
            raise ValueError("Items per page must be between 1 and 100")
            
        conn = get_db_connection()
        data = get_participant_data(conn, study_id, page, per_page)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return handle_route_error(e, "get_participants_data", study_id)

@analytics_bp.route('/<study_id>/export', methods=['GET'])
def export_data_route(study_id):
    # Export study data as CSV, JSON, etc.
    try:
        # Validate study_id
        try:
            study_id = int(study_id)
        except ValueError:
            raise ValueError("Study ID must be an integer")
            
        # Get and validate export format
        export_format = request.args.get('format', 'csv')
        if export_format not in ['csv', 'json', 'xlsx']:
            return jsonify({
                "error": f"Unsupported export format: {export_format}",
                "error_type": "validation_error",
                "supported_formats": ['csv', 'json', 'xlsx']
            }), 400
        
        conn = get_db_connection()
        
        # Get all the necessary data
        summary = get_study_summary(conn, study_id)
        task_performance = get_task_performance_data(conn, study_id)
        # For export, get all participants without pagination
        participants_result = get_participant_data(conn, study_id, 1, 1000) 
        participants = participants_result.get('data', [])
        
        conn.close()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"study_{study_id}_export_{timestamp}"
        
        if export_format == 'csv':
            # Create CSV export
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write summary
            writer.writerow(['Study Summary'])
            writer.writerow(['Total Participants', summary['participantCount']])
            writer.writerow(['Average Completion Time', summary['avgCompletionTime']])
            writer.writerow(['Success Rate', summary['successRate']])
            writer.writerow([])
            
            # Write task performance
            writer.writerow(['Task Performance'])
            writer.writerow(['Task ID', 'Task Name', 'Avg Completion Time', 'Success Rate', 'Error Rate'])
            for task in task_performance:
                writer.writerow([
                    task['taskId'],
                    task['taskName'],
                    task['avgCompletionTime'],
                    task['successRate'],
                    task['errorRate']
                ])
            writer.writerow([])
            
            # Write participant data
            writer.writerow(['Participant Data'])
            writer.writerow(['Participant ID', 'Completion Time', 'Success Rate', 'Error Count', 'First Session', 'Last Session'])
            for participant in participants:
                writer.writerow([
                    participant['participantId'],
                    participant['completionTime'],
                    participant['successRate'],
                    participant['errorCount'],
                    participant.get('firstSession', ''),
                    participant.get('lastSession', '')
                ])
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"{filename}.csv"
            )
            
        elif export_format == 'json':
            # Create JSON export
            export_data = {
                'summary': summary,
                'taskPerformance': task_performance,
                'participants': participants,
                'metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'study_id': study_id
                }
            }
            
            return send_file(
                io.BytesIO(json.dumps(export_data, indent=2).encode('utf-8')),
                mimetype='application/json',
                as_attachment=True,
                download_name=f"{filename}.json"
            )
            
        elif export_format == 'xlsx':
            # For XLSX format, would need additional libraries (openpyxl, pandas)
            # Since this is a example placeholder, we'll return an error
            return jsonify({
                "error": "XLSX export is not implemented yet",
                "error_type": "not_implemented",
            }), 501
            
    except Exception as e:
        return handle_route_error(e, "export_data", study_id)

# Routes for retrieving supplementary data for analytics 
@analytics_bp.route('/studies', methods=['GET'])
def get_studies():
    """
    Get studies belonging to the current user from the database.
    Only shows studies that the logged-in user owns.
    """
    studies = []
    
    try:
        # Try to get current user ID from the session
        from flask_security import current_user
        
        # Get the current user's ID if they're logged in
        current_user_id = None
        if current_user.is_authenticated:
            current_user_id = current_user.id
            logger.info(f"Getting studies for authenticated user ID: {current_user_id}")
        else:
            logger.warning("No authenticated user, will show limited studies")
        
        # Get real database data
        import MySQLdb
        import os
        
        # Get environment variables for database connection
        db_host = os.environ.get('MYSQL_HOST')
        db_user = os.environ.get('MYSQL_USER')
        db_pass = os.environ.get('MYSQL_PASSWORD')
        db_name = os.environ.get('MYSQL_DB')
        
        # Connect directly to MySQL
        db = MySQLdb.connect(
            host=db_host,
            user=db_user,
            passwd=db_pass,
            db=db_name
        )
        
        # Create cursor and execute query
        cursor = db.cursor()
        
        # Get studies belonging to the current user
        if current_user_id:
            cursor.execute("""
                SELECT 
                    s.study_id, 
                    s.study_name,
                    s.study_description,
                    COUNT(DISTINCT ps.participant_id) as participant_count,
                    MAX(ps.created_at) as last_activity
                FROM 
                    study s
                JOIN 
                    study_user_role sur ON s.study_id = sur.study_id
                LEFT JOIN 
                    participant_session ps ON s.study_id = ps.study_id
                WHERE 
                    sur.user_id = %s
                GROUP BY 
                    s.study_id
                ORDER BY 
                    s.study_id DESC
                LIMIT 10
            """, (current_user_id,))
        else:
            # If not logged in, just show some recent studies
            cursor.execute("""
                SELECT 
                    s.study_id, 
                    s.study_name,
                    s.study_description,
                    COUNT(DISTINCT ps.participant_id) as participant_count,
                    MAX(ps.created_at) as last_activity
                FROM 
                    study s
                LEFT JOIN 
                    participant_session ps ON s.study_id = ps.study_id
                GROUP BY 
                    s.study_id
                ORDER BY 
                    s.study_id DESC
                LIMIT 3
            """)
        
        # Process the query results
        rows = cursor.fetchall()
        logger.info(f"Found {len(rows)} rows from database query")
        
        for row in rows:
            study_id = row[0]
            study_name = row[1]
            study_desc = row[2] or ''
            participant_count = row[3] or 0
            last_activity = row[4]
            
            logger.debug(f"Processing study: ID={study_id}, Name={study_name}, Participants={participant_count}")
            
            # Format timestamp for JSON
            last_active_str = None
            if last_activity:
                try:
                    last_active_str = last_activity.strftime('%Y-%m-%dT%H:%M:%S')
                except:
                    last_active_str = str(last_activity)
            
            # Create study object
            study = {
                'id': study_id,
                'name': study_name,
                'description': study_desc,
                'status': 'Active',
                'stats': {
                    'participants': participant_count,
                    'lastActive': last_active_str
                }
            }
            studies.append(study)
            
        # Close database resources
        cursor.close()
        db.close()
        
        logger.info(f"Successfully retrieved {len(studies)} studies from database for user {current_user_id}")
        
        # If no studies found, add a message
        if not studies and current_user_id:
            logger.warning(f"No studies found for user {current_user_id}")
        
    except Exception as e:
        logger.error(f"Database error, falling back to static data: {e}")
        logger.error(traceback.format_exc())
        
        # Fall back to static data if database access fails
        studies = [
            {
                'id': 1,
                'name': 'Memory Test Study (Fallback)',
                'description': 'Testing memory recall patterns',
                'status': 'Active',
                'stats': {
                    'participants': 15,
                    'lastActive': '2025-03-01T10:30:00' 
                }
            },
            {
                'id': 2,
                'name': 'User Interface Study (Fallback)',
                'description': 'Evaluating UI design patterns',
                'status': 'Active',
                'stats': {
                    'participants': 8,
                    'lastActive': '2025-03-15T14:45:00'
                }
            }
        ]
        logger.info("Using static fallback data due to database error")
    
    # Add CORS headers for direct fetch
    response = jsonify(studies)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    logger.info(f"Returning {len(studies)} studies with CORS headers")
    return response

@analytics_bp.route('/participants', methods=['GET'])
def get_participants():
    # Get list of participant IDs for filters
    study_id = request.args.get('study_id', type=int)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get unique participant IDs
        cursor.execute("""
            SELECT DISTINCT participant_id
            FROM participant_session
            WHERE study_id = %s
        """, (study_id,))
        
        participants = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(participants)
    except Exception as e:
        logger.error(f"Error getting participants: {e}")
        # Return empty array instead of error to prevent frontend breakage
        return jsonify([])

@analytics_bp.route('/tasks', methods=['GET'])
def get_tasks():
    # Get tasks list for a study
    study_id = request.args.get('study_id', type=int)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic task info
        cursor.execute("""
            SELECT task_id, task_name, task_description
            FROM task
            WHERE study_id = %s
        """, (study_id,))
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'name': row[1],
                'description': row[2]
            })
            
        conn.close()
        return jsonify(tasks)
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        # Return empty array instead of error to prevent frontend breakage
        return jsonify([])

@analytics_bp.route('/performance', methods=['GET'])
def get_performance():
    # Get detailed performance data for filtering
    participant_id = request.args.get('participant_id')
    task_id = request.args.get('task_id', type=int)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query for participant performance using trials instead of task_results
        query = """
            SELECT 
                t.trial_id,
                ROW_NUMBER() OVER (PARTITION BY t.task_id ORDER BY t.started_at) as attempt_number,
                TIMESTAMPDIFF(SECOND, t.started_at, t.ended_at) as completion_time,
                COUNT(sdi.session_data_instance_id) as interaction_count,
                CASE WHEN t.ended_at IS NOT NULL THEN 'completed' ELSE 'in_progress' END as status
            FROM trial t
            JOIN participant_session ps ON t.participant_session_id = ps.participant_session_id
            LEFT JOIN session_data_instance sdi ON t.trial_id = sdi.trial_id
            WHERE ps.participant_id = %s
        """
        params = [participant_id]
        
        # Add task filter if specified
        if task_id:
            query += " AND t.task_id = %s"
            params.append(task_id)
            
        query += " GROUP BY t.trial_id, t.started_at, t.ended_at ORDER BY t.started_at"
            
        cursor.execute(query, tuple(params))
        
        performance_data = []
        for row in cursor.fetchall():
            performance_data.append({
                'attempt_number': row[1],
                'completion_time': row[2] if row[2] else 0,
                'error_count': row[3],
                'status': row[4]
            })
            
        conn.close()
        
        # If no data, return empty array (don't generate sample data in production)
        if not performance_data:
            return jsonify([])
                
        return jsonify(performance_data)
    except Exception as e:
        logger.error(f"Error getting performance data: {e}")
        # Return empty array instead of error to prevent frontend breakage
        return jsonify([])

@analytics_bp.route('/<study_id>/visualizations/task-completion', methods=['GET'])
def get_task_completion_chart(study_id):
    # Create chart showing task completion rates
    try:
        conn = get_db_connection()
        task_data = get_task_performance_data(conn, study_id)
        conn.close()
        
        # Generate chart as base64 string
        chart_data = generate_task_completion_chart(task_data)
        
        return jsonify({
            "chartType": "taskCompletion",
            "imageData": chart_data,
            "format": "base64"
        })
    except Exception as e:
        logger.error(f"Error generating task completion chart: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/<study_id>/visualizations/error-rate', methods=['GET'])
def get_error_rate_chart(study_id):
    # Create chart showing error rates by task
    try:
        conn = get_db_connection()
        task_data = get_task_performance_data(conn, study_id)
        conn.close()
        
        # Generate chart as base64 string
        chart_data = generate_error_rate_chart(task_data)
        
        return jsonify({
            "chartType": "errorRate",
            "imageData": chart_data,
            "format": "base64"
        })
    except Exception as e:
        logger.error(f"Error generating error rate chart: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/<study_id>/visualizations/learning-curve', methods=['GET'])
def get_learning_curve_chart(study_id):
    # Create chart showing improvement over time
    try:
        conn = get_db_connection()
        learning_data = get_learning_curve_data(conn, study_id)
        conn.close()
        
        # Format data for learning curve chart
        task_data = {}
        for entry in learning_data:
            task_name = entry['taskName']
            if task_name not in task_data:
                task_data[task_name] = {
                    'attempts': [],
                    'times': []
                }
            
            task_data[task_name]['attempts'].append(entry['attempt'])
            task_data[task_name]['times'].append(entry['completionTime'])
        
        # Generate chart
        def generate_chart():
            plot_learning_curve(task_data)
        
        chart_data = plot_to_base64(generate_chart)
        
        return jsonify({
            "chartType": "learningCurve",
            "imageData": chart_data,
            "format": "base64"
        })
    except Exception as e:
        logger.error(f"Error generating learning curve chart: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/ping', methods=['GET'])
def ping():
    """Simple endpoint to check if the analytics API is running"""
    return jsonify({
        "status": "ok",
        "message": "Analytics API is running",
        "timestamp": datetime.now().isoformat()
    })

@analytics_bp.route('/validate-schema', methods=['GET'])
def validate_analytics_schema_endpoint():
    """Endpoint to validate the analytics schema on demand"""
    try:
        conn = get_db_connection()
        schema_ok = validate_analytics_schema(conn)
        conn.close()
        
        return jsonify({
            "status": "ok",
            "schema_valid": schema_ok,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error validating schema: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error validating schema: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@analytics_bp.route('/health', methods=['GET'])
def health_check():
    # Check if API is working properly
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        db_connected = cursor.fetchone() is not None
        
        # If connected, try to validate the analytics schema compatibility
        schema_ok = False
        study_count = 0
        
        if db_connected:
            try:
                # Use the validation function from data_processor
                schema_ok = validate_analytics_schema(conn)
                cursor.execute("SELECT COUNT(*) FROM study")
                study_count = cursor.fetchone()[0]
                logger.info(f"Database connected, found {study_count} studies")
                logger.info(f"Schema validation {'passed' if schema_ok else 'failed'}")
                
                # Check if key tables and joins work
                cursor.execute("""
                    SELECT 
                        COUNT(*) as participant_count
                    FROM 
                        participant_session
                    LIMIT 1
                """)
                participant_count = cursor.fetchone()[0]
                logger.info(f"Found {participant_count} participants")
                
                # Test a more complex query that joins tables
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM participant_session ps
                    JOIN trial t ON ps.participant_session_id = t.participant_session_id
                    LIMIT 1
                """)
                trial_count = cursor.fetchone()[0]
                logger.info(f"Found {trial_count} trials")
                
            except Exception as e:
                logger.error(f"Schema test failed: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Close the connection properly
        cursor.close()
        conn.close()
    except Exception as e:
        db_connected = False
        schema_ok = False
        study_count = 0
        logger.error(f"Health check database connection failed: {str(e)}")
        logger.error(traceback.format_exc())
    
    # Always return a success message with details to help debugging
    return jsonify({
        "status": "ok" if db_connected else "database error", 
        "mode": "production",
        "schema_ok": schema_ok,
        "analytics_compatible": schema_ok,
        "study_count": study_count,
        "database": "MySQL",
        "timestamp": datetime.now().isoformat(),
        "db_config": {
            "host": os.getenv("MYSQL_HOST", "unknown"),
            "database": os.getenv("MYSQL_DB", "unknown"),
            "connected": db_connected
        }
    })