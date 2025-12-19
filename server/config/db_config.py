"""
Database configuration file
Update these settings to match your MySQL server configuration
"""
import mysql.connector
from mysql.connector import pooling

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'phuoc@2209',  # Update with your MySQL password
    'database': 'battleship',
    'port': 3306,
    'raise_on_warnings': True,
    'autocommit': False
}

# Connection pool settings
POOL_CONFIG = {
    'pool_name': 'battleship_pool',
    'pool_size': 5,
    'pool_reset_session': True
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        raise
