import sys
import os
from werkzeug.security import generate_password_hash

# Add the parent directory to Python path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import Config

def initialize_database():
    print("Connecting to MySQL server...")
    import mysql.connector
    
    # Connect without database first to create it
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT
        )
        cursor = conn.cursor()
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        print("Please verify that your MySQL server is running and configuration is correct.")
        sys.exit(1)
        
    print("Database connection established.")
    
    # Create database
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
    cursor.execute(f"USE {Config.MYSQL_DB}")
    print(f"Database '{Config.MYSQL_DB}' created/selected.")
    
    # Read schema.sql
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'schema.sql')
    if not os.path.exists(schema_path):
        print(f"Error: schema.sql not found at {schema_path}")
        sys.exit(1)
        
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        
    # Strip SQL comments line-by-line first
    lines = schema_sql.split('\n')
    cleaned_lines = [line for line in lines if not line.strip().startswith('--')]
    cleaned_schema = '\n'.join(cleaned_lines)
    
    # Split schema.sql into individual commands
    # (simple split by semicolon, ignoring empty lines)
    commands = cleaned_schema.split(';')
    for command in commands:
        cleaned = command.strip()
        if cleaned:
            try:
                cursor.execute(cleaned)
            except mysql.connector.Error as err:
                # If command is database creation and we already did it, ignore
                if "CREATE DATABASE" in cleaned.upper():
                    continue
                print(f"Error executing command: {cleaned}\nError: {err}")
                sys.exit(1)
                
    conn.commit()
    print("Schema tables created successfully.")
    
    # Check if data already exists in login table
    cursor.execute("SELECT COUNT(*) FROM login")
    (login_count,) = cursor.fetchone()
    
    if login_count > 0:
        print("Database already contains records. Skipping sample data population.")
        cursor.close()
        conn.close()
        return

    print("Populating sample data...")
    
    # Sample logins to insert
    # password_hash for the passwords: 'admin123', 'manager123', 'sarah123', 'james123', etc.
    logins = [
        ('admin', generate_password_hash('admin123'), 'Admin'),
        ('manager', generate_password_hash('manager123'), 'Manager'),
        ('sarah', generate_password_hash('sarah123'), 'Employee'),
        ('james', generate_password_hash('james123'), 'Employee'),
        ('emily', generate_password_hash('emily123'), 'Employee'),
        ('michael', generate_password_hash('michael123'), 'Employee'),
        ('priya', generate_password_hash('priya123'), 'Employee')
    ]
    
    # Insert logins and keep track of IDs
    login_ids = {}
    for username, p_hash, role in logins:
        cursor.execute(
            "INSERT INTO login (username, password, role) VALUES (%s, %s, %s)",
            (username, p_hash, role)
        )
        login_ids[username] = cursor.lastrowid
        
    print("Inserted logins.")
    
    # Insert Employees (only for the employees and managers if we want, but the prompt says 5 employees. Let's create employee records for the 5 employees. The manager can have an employee record as well, or just login. Let's make employee records for the 5 employees and the manager if they have fields, but let's check prompt fields: Name, Email, Phone, Department, Designation, login_id. Let's insert the 5 employees)
    employees = [
        ('Sarah Chen', 'sarah.chen@company.com', '+1-555-0101', 'Engineering', 'Senior Developer', login_ids['sarah']),
        ('James Wilson', 'james.wilson@company.com', '+1-555-0102', 'Marketing', 'Marketing Manager', login_ids['james']),
        ('Emily Rodriguez', 'emily.rodriguez@company.com', '+1-555-0103', 'Design', 'UI/UX Designer', login_ids['emily']),
        ('Michael Brown', 'michael.brown@company.com', '+1-555-0104', 'Sales', 'Sales Executive', login_ids['michael']),
        ('Priya Sharma', 'priya.sharma@company.com', '+1-555-0105', 'HR', 'HR Coordinator', login_ids['priya'])
    ]
    
    employee_ids = {}
    for name, email, phone, dept, desig, l_id in employees:
        cursor.execute(
            "INSERT INTO employee (name, email, phone, department, designation, login_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, email, phone, dept, desig, l_id)
        )
        # Store by name for easy mapping to tasks
        employee_ids[name] = cursor.lastrowid
        
    print("Inserted employees.")
    
    # Insert 10 tasks mapped to the employee IDs
    tasks = [
        ("Implement user authentication API", "Build JWT-based authentication endpoints for the mobile app", employee_ids["Sarah Chen"], "High", "In Progress", "2026-07-15"),
        ("Design Q3 marketing campaign", "Create visual assets and copy for the summer campaign launch", employee_ids["James Wilson"], "High", "Pending", "2026-07-20"),
        ("Redesign onboarding screens", "Update the onboarding flow with new brand guidelines", employee_ids["Emily Rodriguez"], "Medium", "In Progress", "2026-07-18"),
        ("Close enterprise deal with Acme Corp", "Follow up with procurement team and finalize contract terms", employee_ids["Michael Brown"], "High", "Pending", "2026-07-12"),
        ("Conduct employee satisfaction survey", "Distribute and collect responses for the quarterly engagement survey", employee_ids["Priya Sharma"], "Medium", "Completed", "2026-07-05"),
        ("Fix database performance issues", "Optimize slow queries and add indexes to the production database", employee_ids["Sarah Chen"], "High", "Completed", "2026-07-08"),
        ("Prepare financial audit report", "Compile financial statements for the external audit team", employee_ids["James Wilson"], "Medium", "Pending", "2026-07-25"),
        ("Set up CI/CD pipeline", "Automate build and deployment process using GitHub Actions", employee_ids["Emily Rodriguez"], "High", "Pending", "2026-07-14"),
        ("Update privacy policy", "Review and update privacy policy document for compliance with GDPR", employee_ids["Michael Brown"], "Low", "Pending", "2026-07-30"),
        ("Write technical documentation", "Document API endpoints and system architecture for onboarding", employee_ids["Priya Sharma"], "Medium", "In Progress", "2026-07-22")
    ]
    
    for title, desc, emp_id, priority, status, due_date in tasks:
        cursor.execute(
            "INSERT INTO tasks (title, description, assigned_to, priority, status, due_date) VALUES (%s, %s, %s, %s, %s, %s)",
            (title, desc, emp_id, priority, status, due_date)
        )
        
    print("Inserted tasks.")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized and sample data populated successfully!")

if __name__ == '__main__':
    initialize_database()
