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

@analytics_bp.route('/<study_id>/summary', methods=['GET'])
def get_study_summary_route(study_id):
    """Get summary metrics for a study"""
    try:
        conn = get_db_connection()
        summary = get_study_summary(conn, study_id)
        conn.close()
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Unexpected error in summary stats for study {study_id}: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/summary', methods=['GET'])
def get_summary_stats_by_param():
    """Get summary metrics for dashboard cards using query parameter"""
    study_id = request.args.get('study_id', type=int)
    try:
        return get_study_summary_route(study_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/<study_id>/learning-curve', methods=['GET'])
def get_learning_curve_route(study_id):
    """Get learning curve data for a study"""
    try:
        conn = get_db_connection()
        data = get_learning_curve_data(conn, study_id)
        conn.close()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting learning curve data: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/learning-curve', methods=['GET'])
def get_learning_curve_by_param():
    """Get learning curve data using query parameter"""
    study_id = request.args.get('study_id', type=int)
    try:
        return get_learning_curve_route(study_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/<study_id>/task-performance', methods=['GET'])
def get_task_performance_route(study_id):
    """Get task performance data for a study"""
    try:
        conn = get_db_connection()
        data = get_task_performance_data(conn, study_id)
        conn.close()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting task performance data: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/task-comparison', methods=['GET'])
def get_task_comparison():
    """Get data for the task performance comparison chart using query parameter"""
    study_id = request.args.get('study_id', type=int)
    try:
        return get_task_performance_route(study_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/<study_id>/participants', methods=['GET'])
def get_participants_route(study_id):
    """Get participant data for a study"""
    try:
        conn = get_db_connection()
        data = get_participant_data(conn, study_id)
        conn.close()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting participant data: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/<study_id>/export', methods=['GET'])
def export_data_route(study_id):
    """Export study data in specified format"""
    try:
        export_format = request.args.get('format', 'csv')
        
        conn = get_db_connection()
        
        # Get all the necessary data
        summary = get_study_summary(conn, study_id)
        task_performance = get_task_performance_data(conn, study_id)
        participants = get_participant_data(conn, study_id)
        
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
            writer.writerow(['Participant ID', 'Completion Time', 'Success Rate', 'Error Count'])
            for participant in participants:
                writer.writerow([
                    participant['participantId'],
                    participant['completionTime'],
                    participant['successRate'],
                    participant['errorCount']
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
                'participants': participants
            }
            
            return send_file(
                io.BytesIO(json.dumps(export_data, indent=2).encode('utf-8')),
                mimetype='application/json',
                as_attachment=True,
                download_name=f"{filename}.json"
            )
            
        else:
            return jsonify({"error": f"Unsupported export format: {export_format}"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Routes for retrieving supplementary data for analytics 
@analytics_bp.route('/studies', methods=['GET'])
def get_studies():
    """Get list of available studies for the selector dropdown"""
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
    """Get list of participant IDs for a study"""
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
    """Get list of tasks for a study"""
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
    """Get performance data for a specific participant or task"""
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
    """Generate task completion chart for a study"""
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
    """Generate error rate chart for a study"""
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
    """Generate learning curve chart for a study"""
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
    """API health check endpoint for monitoring"""
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