import mysql.connector
from config import Config


def get_connection():
    """Open and return a new MySQL database connection."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )


def execute_query(query, params=None, fetch=False, fetchone=False):
    """
    Execute a SQL query and return results or last insert ID.

    Args:
        query    (str):   SQL statement to execute.
        params   (tuple): Parameters for the query (prevents SQL injection).
        fetch    (bool):  If True, fetch all rows as list of dicts.
        fetchone (bool):  If True, fetch a single row as dict.

    Returns:
        list | dict | int | None
    """
    conn   = get_connection()
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
