import sqlite3
import os
from pathlib import Path
from local_config import DB_PATH

def init_db():
    """Initialize the SQLite database with schema"""
    
    # Make sure the database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript('''
    -- Drop tables if they exist
    DROP TABLE IF EXISTS participants;
    DROP TABLE IF EXISTS tasks;
    DROP TABLE IF EXISTS performance;
    DROP TABLE IF EXISTS interactions;
    DROP TABLE IF EXISTS studies;
    
    -- Create studies table
    CREATE TABLE studies (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT
    );
    
    -- Create participants table
    CREATE TABLE participants (
        id INTEGER PRIMARY KEY,
        user_id TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        experience_level TEXT,
        created_at TEXT
    );
    
    -- Create tasks table
    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        expected_completion_time INTEGER,
        complexity TEXT
    );
    
    -- Create performance table
    CREATE TABLE performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_id INTEGER,
        task_id INTEGER,
        trial INTEGER,
        completion_time INTEGER,
        error_count INTEGER,
        success INTEGER,
        timestamp TEXT,
        FOREIGN KEY (participant_id) REFERENCES participants (id),
        FOREIGN KEY (task_id) REFERENCES tasks (id)
    );
    
    -- Create interactions table
    CREATE TABLE interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_id INTEGER,
        task_id INTEGER,
        trial INTEGER,
        event_type TEXT,
        element TEXT,
        timestamp TEXT,
        x_position INTEGER,
        y_position INTEGER,
        duration INTEGER,
        FOREIGN KEY (participant_id) REFERENCES participants (id),
        FOREIGN KEY (task_id) REFERENCES tasks (id)
    );
    ''')
    
    # Insert sample data
    cursor.executescript('''
    -- Insert sample studies
    INSERT INTO studies (id, name, description) VALUES
        (1, 'Navigation Study', 'Testing website navigation efficiency'),
        (2, 'Form Input Study', 'Testing form input experience'),
        (3, 'Mobile Usability Study', 'Testing mobile interface usability');
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    # Check if database file already exists
    if os.path.exists(DB_PATH):
        confirm = input(f"Database file already exists at {DB_PATH}. Overwrite? (y/n): ")
        if confirm.lower() != 'y':
            print("Database initialization cancelled.")
            exit()
    
    # Initialize the database
    init_db()
    
    # Import and populate with mock data
    print("Populating database with mock data...")
    from mock_data import get_all_mock_data
    
    mock_data = get_all_mock_data()
    
    # Connect to the database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Insert mock participants
    for p in mock_data["participants"]:
        cursor.execute('''
        INSERT INTO participants (id, user_id, age, gender, experience_level, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (p["id"], p["user_id"], p["age"], p["gender"], p["experience_level"], p["created_at"]))
    
    # Insert mock tasks
    for t in mock_data["tasks"]:
        cursor.execute('''
        INSERT INTO tasks (id, name, description, expected_completion_time, complexity)
        VALUES (?, ?, ?, ?, ?)
        ''', (t["id"], t["name"], t["description"], t["expected_completion_time"], t["complexity"]))
    
    # Insert mock performance data
    for perf in mock_data["performance"]:
        cursor.execute('''
        INSERT INTO performance (participant_id, task_id, trial, completion_time, error_count, success, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (perf["participant_id"], perf["task_id"], perf["trial"], 
              perf["completion_time"], perf["error_count"], 1 if perf["success"] else 0, perf["timestamp"]))
    
    # Insert mock interaction data (just a sample)
    for i, interaction in enumerate(mock_data["interactions"]):
        if i >= 1000:  # Limit to 1000 interactions to keep the database small
            break
        cursor.execute('''
        INSERT INTO interactions (participant_id, task_id, trial, event_type, element, timestamp, x_position, y_position, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (interaction["participant_id"], interaction["task_id"], interaction["trial"],
              interaction["event_type"], interaction["element"], interaction["timestamp"],
              interaction["x_position"], interaction["y_position"], interaction["duration"]))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database populated with mock data!")