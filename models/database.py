import mysql.connector
from mysql.connector import pooling
from config import Config

# Connection Pool for better performance
connection_pool = None

def init_db():
    """Initialize database connection pool"""
    global connection_pool
    try:
        connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="opd_pool",
            pool_size=5,
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        print("✅ Database connection pool created successfully")
    except mysql.connector.Error as err:
        print(f"❌ Database connection failed: {err}")
        raise

def get_db_connection():
    """Get connection from pool"""
    try:
        return connection_pool.get_connection()
    except mysql.connector.Error as err:
        print(f"❌ Error getting connection: {err}")
        raise

def execute_query(query, params=None, fetch=False):
    """Execute SQL query with proper connection handling"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"❌ Query error: {err}")
        raise
    finally:
        cursor.close()
        conn.close()