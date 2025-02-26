import mysql.connector
from mysql.connector import pooling
import time
from contextlib import contextmanager
from local_config import DB_CONFIG

# Set up connection pool for better performance
try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="fulcrum_pool",
        pool_size=5,
        **DB_CONFIG
    )
except mysql.connector.Error as err:
    print(f"Error creating connection pool: {err}")
    connection_pool = None


def get_db_connection():
    """Get database connection with retry logic"""
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        try:
            # Try pool first, fall back to direct connection
            if connection_pool:
                return connection_pool.get_connection()
            else:
                return mysql.connector.connect(**DB_CONFIG)
        except mysql.connector.Error as err:
            attempts += 1
            if attempts >= max_attempts:
                raise Exception(f"Failed to connect to database after {max_attempts} attempts: {err}")
            time.sleep(1)  # Wait before retry


@contextmanager
def db_cursor():
    """Create a database cursor that handles connections and transactions"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
        yield cursor
        conn.commit()  # Auto-commit on success
    except mysql.connector.Error as err:
        if conn:
            conn.rollback()  # Rollback on error
        raise Exception(f"Database error: {err}")
    finally:
        # Always clean up resources
        if 'cursor' in locals() and cursor:
            cursor.close()
        if conn:
            conn.close()


def execute_query(query, params=None, fetch_one=False):
    """Run a query and return results"""
    with db_cursor() as cursor:
        cursor.execute(query, params or ())
        
        # Handle queries that don't return results (like INSERT)
        if cursor.description is None:
            return None
            
        # Return a single row or all rows based on parameter
        if fetch_one:
            return cursor.fetchone()
        else:
            return cursor.fetchall()


def test_connection():
    """Check if database connection works"""
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return bool(result and result.get('1') == 1)
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False


def get_schema():
    """Get database structure for debugging"""
    schema = {}
    try:
        with db_cursor() as cursor:
            # Get all table names
            cursor.execute(
                "SELECT TABLE_NAME FROM information_schema.tables "
                f"WHERE TABLE_SCHEMA = '{DB_CONFIG['database']}'"
            )
            tables = [row['TABLE_NAME'] for row in cursor.fetchall()]
            
            # Get column details for each table
            for table in tables:
                cursor.execute(
                    "SELECT COLUMN_NAME, DATA_TYPE, COLUMN_KEY, EXTRA "
                    "FROM information_schema.columns "
                    f"WHERE TABLE_SCHEMA = '{DB_CONFIG['database']}' "
                    f"AND TABLE_NAME = '{table}'"
                )
                schema[table] = cursor.fetchall()
        
        return schema
    except Exception as e:
        print(f"Error getting schema: {e}")
        return None


if __name__ == "__main__":
    # Self-test when run as a script
    if test_connection():
        print("Database connection successful!")
        
        # Display database structure
        schema = get_schema()
        if schema:
            print("\nDatabase Schema:")
            for table, columns in schema.items():
                print(f"\n{table}:")
                for column in columns:
                    pk = "PK" if column['COLUMN_KEY'] == 'PRI' else ""
                    auto = "AUTO_INCREMENT" if column['EXTRA'] == 'auto_increment' else ""
                    print(f"  - {column['COLUMN_NAME']} ({column['DATA_TYPE']}) {pk} {auto}")
    else:
        print("Database connection failed.")