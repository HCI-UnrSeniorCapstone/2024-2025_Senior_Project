#!/usr/bin/env python3
"""
Mock Data Generator for Fulcrum Analytics Workspace
Generates test data for studies, tasks, sessions, and task results
"""

import mysql.connector
import random
import datetime
import time
import argparse
from faker import Faker

# Setup faker for generating realistic text
fake = Faker()

# Database connection settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',
    'database': 'fulcrum_analytics'
}

# Default generation parameters
NUM_STUDIES = 5
NUM_TASKS_PER_STUDY = 3
NUM_PARTICIPANTS = 20
MAX_SESSIONS_PER_PARTICIPANT = 3
MAX_ATTEMPTS_PER_TASK = 3

def create_database():
    """Set up database schema from scratch"""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Create studies table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS studies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status ENUM('draft', 'active', 'completed', 'archived') DEFAULT 'active'
        )
        """)
        
        # Create tasks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            study_id INT NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (study_id) REFERENCES studies(id)
        )
        """)
        
        # Create sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            study_id INT NOT NULL,
            participant_id VARCHAR(50) NOT NULL,
            start_time INT NOT NULL,
            end_time INT,
            status ENUM('in_progress', 'completed', 'failed', 'abandoned') DEFAULT 'in_progress',
            FOREIGN KEY (study_id) REFERENCES studies(id)
        )
        """)
        
        # Create task_results table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id INT NOT NULL,
            task_id INT NOT NULL,
            attempt_number INT DEFAULT 1,
            start_time INT NOT NULL,
            end_time INT,
            completion_time FLOAT,
            error_count INT DEFAULT 0,
            status ENUM('in_progress', 'completed', 'failed', 'skipped') DEFAULT 'in_progress',
            FOREIGN KEY (session_id) REFERENCES sessions(id),
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database and tables created successfully")
    except mysql.connector.Error as err:
        print(f"Database creation error: {err}")

def generate_studies(num_studies):
    """Create mock study records"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM task_results")
    cursor.execute("DELETE FROM sessions")
    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM studies")
    
    # Create new studies
    studies = []
    for i in range(num_studies):
        name = f"Study {i+1}: {fake.catch_phrase()}"
        description = fake.paragraph()
        status = random.choice(['draft', 'active', 'active', 'active', 'completed', 'archived'])
        
        cursor.execute(
            "INSERT INTO studies (name, description, status) VALUES (%s, %s, %s)",
            (name, description, status)
        )
        study_id = cursor.lastrowid
        studies.append(study_id)
        
        print(f"Created study: {name} (ID: {study_id})")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return studies

def generate_tasks(study_ids, tasks_per_study):
    """Create tasks for each study"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    tasks = []
    for study_id in study_ids:
        for i in range(tasks_per_study):
            # Different task types for variety
            task_type = random.choice(['search', 'navigation', 'form', 'interaction', 'reading'])
            name = f"Task {i+1}: {task_type.capitalize()} task"
            description = fake.paragraph()
            
            cursor.execute(
                "INSERT INTO tasks (study_id, name, description) VALUES (%s, %s, %s)",
                (study_id, name, description)
            )
            task_id = cursor.lastrowid
            tasks.append((study_id, task_id))
            
            print(f"Created task: {name} for study {study_id} (ID: {task_id})")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return tasks

def generate_sessions_and_results(tasks, num_participants, max_sessions, max_attempts):
    """Create sessions and task results with realistic patterns"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Organize tasks by study
    tasks_by_study = {}
    for study_id, task_id in tasks:
        if study_id not in tasks_by_study:
            tasks_by_study[study_id] = []
        tasks_by_study[study_id].append(task_id)
    
    # Create participant IDs
    participants = [f"P{str(i+1).zfill(3)}" for i in range(num_participants)]
    
    # Use last 30 days for data range
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=30)
    
    for study_id, task_ids in tasks_by_study.items():
        if len(task_ids) == 0:
            continue
            
        # Assign some participants to each study
        study_participants = random.sample(
            participants, 
            random.randint(max(3, len(participants) // 2), len(participants))
        )
        
        for participant_id in study_participants:
            # Generate 1-3 sessions per participant
            for _ in range(random.randint(1, max_sessions)):
                # Create session with random date in the range
                random_date = start_date + datetime.timedelta(
                    seconds=random.randint(0, int((end_date - start_date).total_seconds()))
                )
                start_time = int(random_date.timestamp())
                
                # Most sessions should be completed
                is_completed = random.random() < 0.9
                
                if is_completed:
                    # Sessions last 10-60 minutes
                    duration = random.randint(10 * 60, 60 * 60)
                    end_time = start_time + duration
                    status = 'completed'
                else:
                    # Some sessions are abandoned mid-way
                    if random.random() < 0.5:
                        duration = random.randint(5 * 60, 30 * 60)
                        end_time = start_time + duration
                    else:
                        end_time = None
                    status = random.choice(['in_progress', 'failed', 'abandoned'])
                
                cursor.execute(
                    "INSERT INTO sessions (study_id, participant_id, start_time, end_time, status) VALUES (%s, %s, %s, %s, %s)",
                    (study_id, participant_id, start_time, end_time, status)
                )
                session_id = cursor.lastrowid
                
                print(f"Created session for participant {participant_id} in study {study_id} (ID: {session_id})")
                
                # Track time within the session
                task_start_time = start_time
                
                for task_id in task_ids:
                    # Create 1-3 attempts per task (for learning curve data)
                    attempts = random.randint(1, max_attempts)
                    
                    for attempt in range(1, attempts + 1):
                        # Improve with each attempt (learning effect)
                        base_time = random.randint(60, 300)  # 1-5 minutes per task
                        learning_factor = max(0.6, 1.0 - (attempt - 1) * 0.2)  # 20% faster each try
                        task_duration = base_time * learning_factor
                        
                        task_end_time = task_start_time + int(task_duration)
                        
                        # Fewer errors with each attempt
                        base_errors = random.randint(0, 10)
                        error_count = int(base_errors * learning_factor)
                        
                        # Higher success rate with each attempt
                        success_prob = min(0.95, 0.6 + (attempt - 1) * 0.15)
                        task_completed = random.random() < success_prob
                        
                        if task_completed:
                            task_status = 'completed'
                            task_completion_time = task_duration
                        else:
                            task_status = random.choice(['failed', 'skipped'])
                            # Partial time for incomplete tasks
                            task_completion_time = task_duration * random.uniform(0.3, 0.8) if random.random() < 0.7 else None
                        
                        # Skip some results for incomplete sessions
                        if status != 'completed' and random.random() < 0.3:
                            continue
                            
                        cursor.execute(
                            """INSERT INTO task_results 
                               (session_id, task_id, attempt_number, start_time, end_time, completion_time, error_count, status) 
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                            (session_id, task_id, attempt, task_start_time, task_end_time, task_completion_time, error_count, task_status)
                        )
                        
                        # Add time between tasks
                        task_start_time = task_end_time + random.randint(10, 60)  # 10-60 second break
                        
                        # Stop if beyond session end time
                        if end_time and task_start_time > end_time:
                            break
                    
                    # Stop if beyond session end time
                    if end_time and task_start_time > end_time:
                        break
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Generated all sessions and task results")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate mock data for Fulcrum Analytics')
    parser.add_argument('--reset', action='store_true', help='Reset and recreate the database structure')
    parser.add_argument('--studies', type=int, default=5, help='Number of studies to create')
    parser.add_argument('--tasks', type=int, default=3, help='Number of tasks per study')
    parser.add_argument('--participants', type=int, default=20, help='Number of participants')
    args = parser.parse_args()
    
    try:
        # Create database structure if requested
        if args.reset:
            create_database()
        
        # Generate data in sequence
        print("\n=== Generating Studies ===")
        study_ids = generate_studies(args.studies)
        
        print("\n=== Generating Tasks ===")
        tasks = generate_tasks(study_ids, args.tasks)
        
        print("\n=== Generating Sessions and Results ===")
        generate_sessions_and_results(tasks, args.participants, MAX_SESSIONS_PER_PARTICIPANT, MAX_ATTEMPTS_PER_TASK)
        
        print("\n=== Data Generation Complete ===")
        
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()