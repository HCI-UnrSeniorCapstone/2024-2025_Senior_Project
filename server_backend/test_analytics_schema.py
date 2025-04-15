#!/usr/bin/env python3
"""
Quick test for analytics schema validation
"""
import os
import sys
import mysql.connector

# Add the current directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the validation function
from app.utility.analytics.data_processor import validate_analytics_schema

def get_db_connection():
    """Create direct database connection for testing"""
    # Get database credentials from environment
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

def test_schema_validation():
    """Test the analytics schema validation directly"""
    conn = get_db_connection()
    
    if not conn:
        print("Cannot proceed without database connection")
        return False
        
    print("\nTesting analytics schema validation...")
    try:
        schema_valid = validate_analytics_schema(conn)
        
        if schema_valid:
            print("\n✅ SUCCESS: Analytics schema validation passed")
            print("The database schema is compatible with the analytics module")
        else:
            print("\n❌ FAILURE: Analytics schema validation failed")
            print("The database schema is not compatible with the analytics module")
            
        return schema_valid
    except Exception as e:
        print(f"\n❌ ERROR: Schema validation error: {e}")
        import traceback
        print(traceback.format_exc())
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = test_schema_validation()
    sys.exit(0 if success else 1)