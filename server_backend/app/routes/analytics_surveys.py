"""
API routes for survey data access in analytics
"""
from flask import Blueprint, jsonify, current_app
import logging
import json
import os
from app.utility.db_connection import get_db_connection

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint for survey routes
analytics_surveys_bp = Blueprint('analytics_surveys', __name__, url_prefix='/api/analytics')

@analytics_surveys_bp.route('/participant-surveys/<int:study_id>/<int:participant_id>', methods=['GET'])
def get_participant_surveys(study_id, participant_id):
    """Get pre and post survey results for a specific participant"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get participant_session_id for this participant in this study
        cursor.execute("""
            SELECT ps.participant_session_id 
            FROM participant_session ps
            JOIN participant p ON ps.participant_id = p.participant_id
            WHERE p.participant_id = %s AND ps.study_id = %s
            LIMIT 1
        """, (participant_id, study_id))
        
        session_result = cursor.fetchone()
        if not session_result:
            return jsonify({"error": "Participant session not found"}), 404
            
        participant_session_id = session_result[0]  # Index-based access instead of dictionary
        
        # Get pre and post survey results
        cursor.execute("""
            SELECT sr.file_path, sf.form_type 
            FROM survey_results sr
            JOIN survey_form sf ON sr.survey_form_id = sf.survey_form_id
            WHERE sr.participant_session_id = %s
        """, (participant_session_id,))
        
        survey_files = cursor.fetchall()
        
        # Load survey content from files
        survey_data = {"pre": None, "post": None}
        for survey in survey_files:
            try:
                file_path = survey[0]  # Index 0 = file_path
                form_type = survey[1]  # Index 1 = form_type
                
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        survey_data[form_type] = json.load(f)
                        logger.info(f"Loaded {form_type} survey from {file_path}")
                else:
                    logger.warning(f"Survey file not found: {file_path}")
            except Exception as e:
                logger.error(f"Error loading survey file {file_path}: {str(e)}")
        
        return jsonify({"surveys": survey_data}), 200
        
    except Exception as e:
        logger.error(f"Error retrieving participant surveys: {str(e)}")
        return jsonify({"error": f"Failed to retrieve surveys: {str(e)}"}), 500