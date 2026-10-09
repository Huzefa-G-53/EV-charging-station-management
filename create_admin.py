"""
create_admin.py
Run once to create the admin account in the database.
Usage: python create_admin.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from werkzeug.security import generate_password_hash
from database.db_connection import execute_query

ADMIN_NAME     = 'System Administrator'
ADMIN_EMAIL    = 'admin@ev.com'
ADMIN_PASSWORD = 'admin123'


def main():
    # Check if admin already exists
    existing = execute_query(
        'SELECT admin_id FROM admin WHERE email = %s',
        (ADMIN_EMAIL,),
        fetchone=True
    )
    if existing:
        print(f'Admin with email "{ADMIN_EMAIL}" already exists. No action taken.')
        return

    password_hash = generate_password_hash(ADMIN_PASSWORD)
    execute_query(
        'INSERT INTO admin (full_name, email, password_hash) VALUES (%s, %s, %s)',
        (ADMIN_NAME, ADMIN_EMAIL, password_hash)
    )
    print('Admin account created successfully!')
    print(f'  Email   : {ADMIN_EMAIL}')
    print(f'  Password: {ADMIN_PASSWORD}')


if __name__ == '__main__':
    main()
