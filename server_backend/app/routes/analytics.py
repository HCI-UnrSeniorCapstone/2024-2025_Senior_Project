from flask import Blueprint, jsonify, request, send_file
from app.utility.analytics.data_processor import (
    get_study_summary,
    get_learning_curve_data,
    get_task_performance_data,
    get_participant_data
)
from app.utility.db_connection import get_db_connection
import io
import csv
import json
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/<study_id>/summary', methods=['GET'])
def get_study_summary_route(study_id):
    """Get summary metrics for a study"""
    try:
        conn = get_db_connection()
        summary = get_study_summary(conn, study_id)
        conn.close()
        return jsonify(summary)
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