from flask_mysqldb import MySQL

mysql = MySQL()

def get_db_connection():
    return mysql.connection
