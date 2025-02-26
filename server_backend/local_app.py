from flask import Flask, jsonify, request
from flask_cors import CORS
import os

# Import local database module
import local_db

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Routes for analytics data
@app.route('/api/analytics/summary', methods=['GET'])
def get_summary_stats():
    """Get summary statistics for the dashboard"""
    stats = local_db.get_summary_stats()
    return jsonify(stats)

@app.route('/api/analytics/learning-curve', methods=['GET'])
def get_learning_curve():
    """Get learning curve data for visualization"""
    data = local_db.get_learning_curve_data()
    return jsonify(data)

@app.route('/api/analytics/task-comparison', methods=['GET'])
def get_task_comparison():
    """Get task comparison data for visualization"""
    data = local_db.get_task_comparison_data()
    return jsonify(data)

@app.route('/api/studies', methods=['GET'])
def get_studies():
    """Get list of available studies"""
    studies = local_db.get_studies()
    return jsonify(studies)

@app.route('/api/participants', methods=['GET'])
def get_participants():
    """Get list of study participants"""
    study_id = request.args.get('study_id', type=int)
    participants = local_db.get_participants(study_id)
    return jsonify(participants)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get list of tasks"""
    tasks = local_db.get_tasks()
    return jsonify(tasks)

@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get performance data"""
    participant_id = request.args.get('participant_id', type=int)
    task_id = request.args.get('task_id', type=int)
    
    data = local_db.get_performance_data(participant_id, task_id)
    return jsonify(data)

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        "status": "ok", 
        "mode": "local development",
        "database": "SQLite",
        "db_path": str(os.path.abspath(local_db.DB_PATH))
    })

if __name__ == '__main__':
    # Set debug mode for local development
    app.run(debug=True, host='0.0.0.0', port=5000)