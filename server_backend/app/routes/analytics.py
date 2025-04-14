from flask import Blueprint, jsonify, request, send_file, current_app
from app.utility.analytics.data_processor import (
    get_study_summary,
    get_learning_curve_data,
    get_task_performance_data,
    get_participant_data
)
from app.utility.analytics.visualization_helper import (
    plot_to_base64,
    generate_task_completion_chart,
    generate_error_rate_chart,
    calculate_interaction_metrics
)
from app.utility.db_connection import get_db_connection
import io
import csv
import json
import logging
import traceback
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    # Get studies for the dropdown selector
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get studies with participant count and last activity timestamp
        cursor.execute("""
            SELECT id, name, description, status,
                (SELECT COUNT(DISTINCT participant_id) FROM sessions WHERE study_id = studies.id) as participant_count,
                (SELECT MAX(start_time) FROM sessions WHERE study_id = studies.id) as last_activity
            FROM studies
            ORDER BY last_activity DESC
        """)
        
        studies = []
        for row in cursor.fetchall():
            study = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'status': row[3],
                'participant_count': row[4] or 0,
                'last_activity': row[5]
            }
            
            if study['last_activity']:
                # Convert timestamp to ISO format
                timestamp = datetime.fromtimestamp(study['last_activity'])
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
                
            studies.append(study)
        
        conn.close()
        return jsonify(studies)
    except Exception as e:
        logger.error(f"Error fetching studies: {e}")
        return jsonify({"error": str(e)}), 500

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
            FROM sessions
            WHERE study_id = ?
        """, (study_id,))
        
        participants = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(participants)
    except Exception as e:
        logger.error(f"Error getting participants: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/tasks', methods=['GET'])
def get_tasks():
    # Get tasks list for a study
    study_id = request.args.get('study_id', type=int)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic task info
        cursor.execute("""
            SELECT id, name, description
            FROM tasks
            WHERE study_id = ?
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
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/performance', methods=['GET'])
def get_performance():
    # Get detailed performance data for filtering
    participant_id = request.args.get('participant_id')
    task_id = request.args.get('task_id', type=int)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query for participant performance
        query = """
            SELECT 
                tr.attempt_number,
                tr.completion_time,
                tr.error_count,
                tr.status
            FROM task_results tr
            JOIN sessions s ON tr.session_id = s.id
            WHERE s.participant_id = ?
        """
        params = [participant_id]
        
        # Add task filter if specified
        if task_id:
            query += " AND tr.task_id = ?"
            params.append(task_id)
            
        query += " ORDER BY tr.attempt_number"
            
        cursor.execute(query, tuple(params))
        
        performance_data = []
        for row in cursor.fetchall():
            performance_data.append({
                'attempt_number': row[0],
                'completion_time': row[1],
                'error_count': row[2],
                'status': row[3]
            })
            
        conn.close()
        return jsonify(performance_data)
    except Exception as e:
        logger.error(f"Error getting performance data: {e}")
        return jsonify({"error": str(e)}), 500

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

@analytics_bp.route('/health', methods=['GET'])
def health_check():
    # Check if API is working properly
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        db_connected = cursor.fetchone() is not None
        conn.close()
    except Exception:
        db_connected = False
        
    return jsonify({
        "status": "ok" if db_connected else "database error", 
        "mode": "production",
        "database": "MySQL",
        "db_config": {
            "host": "*****", # Redacted for security
            "database": "*****", # Redacted for security
            "connected": db_connected
        }
    })