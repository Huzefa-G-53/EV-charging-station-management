import mysql.connector
from mysql.connector import pooling
from config import Config

_pool = None


def get_connection():
    """
    Get a database connection from the connection pool.
    Initializes the pool on first invocation.
    """
    global _pool
    if _pool is None:
        try:
            _pool = pooling.MySQLConnectionPool(
                pool_name="ev_pool",
                pool_size=5,
                pool_reset_session=True,
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )
        except Exception:
            # Fallback to direct connection if pooling initialization fails
            return mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )
    try:
        return _pool.get_connection()
    except Exception:
        # Fallback to direct connection if pool exhausted
        return mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )


def execute_query(query, params=None, fetch=False, fetchone=False):
    """
    Execute a SQL query using a pooled connection and return results or last insert ID.

    Args:
        query    (str):   SQL statement to execute.
        params   (tuple): Parameters for the query (prevents SQL injection).
        fetch    (bool):  If True, fetch all rows as list of dicts.
        fetchone (bool):  If True, fetch a single row as dict.

    Returns:
        list | dict | int | None
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
        elif fetchone:
            result = cursor.fetchone()
        else:
            conn.commit()
            result = cursor.lastrowid
    finally:
        cursor.close()
        conn.close()
    return result

