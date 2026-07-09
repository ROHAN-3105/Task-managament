import os

class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'dev_secret_key_taskflow_91823102'
    )

    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'Rohan@123')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'task_management')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))