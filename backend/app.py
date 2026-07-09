from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os
import sys

# Ensure backend config is importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import Config

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'static'))
app.config.from_object(Config)

# Database Connection Helper
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            port=app.config['MYSQL_PORT']
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

# Context Processor to make current user details easily accessible in templates
@app.context_processor
def inject_user():
    return dict(
        current_user_role=session.get('role'),
        current_user_name=session.get('name'),
        current_user_username=session.get('username')
    )

# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'login_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator to restrict access to specific roles
def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                flash('Access denied. You do not have permission to view this page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- ROUTES ---

@app.route('/')
def index():
    if 'login_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'login_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if not username or not password or not role:
            flash('All fields are required.', 'danger')
            return render_template('login.html')
            
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed. Please try again later.', 'danger')
            return render_template('login.html')
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM login WHERE username = %s AND role = %s", (username, role))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            # Session handling
            session['login_id'] = user['login_id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            # Fetch Employee Details if applicable
            if role in ['Employee', 'Manager']:
                cursor.execute("SELECT * FROM employee WHERE login_id = %s", (user['login_id'],))
                emp = cursor.fetchone()
                if emp:
                    session['employee_id'] = emp['employee_id']
                    session['name'] = emp['name']
                else:
                    session['name'] = username
            else:
                session['name'] = 'Admin User'
                
            cursor.close()
            conn.close()
            flash(f"Welcome back, {session['name']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            cursor.close()
            conn.close()
            flash('Invalid username, password, or role combination.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    if not conn:
        flash('Failed to fetch dashboard data.', 'danger')
        return render_template('dashboard.html')
        
    cursor = conn.cursor(dictionary=True)
    role = session['role']
    
    # 1. Fetch Metrics Cards Data
    if role in ['Admin', 'Manager']:
        cursor.execute("SELECT COUNT(*) as count FROM employee")
        total_employees = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM tasks")
        total_tasks = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status != 'Completed'")
        pending_tasks = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'Completed'")
        completed_tasks = cursor.fetchone()['count']
    else: # Employee
        emp_id = session.get('employee_id', 0)
        total_employees = 0 # Not applicable for employee dashboard metrics
        
        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE assigned_to = %s", (emp_id,))
        total_tasks = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE assigned_to = %s AND status != 'Completed'", (emp_id,))
        pending_tasks = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE assigned_to = %s AND status = 'Completed'", (emp_id,))
        completed_tasks = cursor.fetchone()['count']
        
    # Calculate Completion percentage
    completion_rate = round((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    # 2. Fetch Chart.js analytics payload
    chart_data = {
        'status_counts': {'Pending': 0, 'In Progress': 0, 'Completed': 0},
        'employee_tasks': []
    }
    
    # Status Breakdown query
    if role in ['Admin', 'Manager']:
        cursor.execute("SELECT status, COUNT(*) as count FROM tasks GROUP BY status")
    else:
        cursor.execute("SELECT status, COUNT(*) as count FROM tasks WHERE assigned_to = %s GROUP BY status", (session.get('employee_id', 0),))
        
    for row in cursor.fetchall():
        chart_data['status_counts'][row['status']] = row['count']
        
    # Employee-wise tasks query (For Admin/Manager charts)
    if role in ['Admin', 'Manager']:
        cursor.execute("""
            SELECT e.name, 
                   SUM(CASE WHEN t.status = 'Pending' THEN 1 ELSE 0 END) as pending,
                   SUM(CASE WHEN t.status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
                   SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM employee e
            LEFT JOIN tasks t ON e.employee_id = t.assigned_to
            GROUP BY e.employee_id, e.name
        """)
        chart_data['employee_tasks'] = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', 
                           total_employees=total_employees,
                           total_tasks=total_tasks,
                           pending_tasks=pending_tasks,
                           completed_tasks=completed_tasks,
                           completion_rate=completion_rate,
                           chart_data=chart_data)

@app.route('/employees')
@login_required
@roles_required('Admin', 'Manager')
def employees():
    conn = get_db_connection()
    if not conn:
        flash('Failed to connect to database.', 'danger')
        return redirect(url_for('dashboard'))
        
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.*, l.username, l.role 
        FROM employee e 
        JOIN login l ON e.login_id = l.login_id
    """)
    emp_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('employees.html', employees=emp_list)

@app.route('/employee/add', methods=['POST'])
@login_required
@roles_required('Admin', 'Manager')
def add_employee():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    department = request.form.get('department')
    designation = request.form.get('designation')
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role', 'Employee')
    
    if not name or not email or not username or not password:
        flash('Name, Email, Username and Password are required.', 'danger')
        return redirect(url_for('employees'))
        
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return redirect(url_for('employees'))
        
    cursor = conn.cursor(dictionary=True)
    
    # Check if username or email already exists
    cursor.execute("SELECT login_id FROM login WHERE username = %s", (username,))
    if cursor.fetchone():
        flash('Username already exists.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('employees'))
        
    cursor.execute("SELECT employee_id FROM employee WHERE email = %s", (email,))
    if cursor.fetchone():
        flash('Email already in use.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('employees'))
        
    try:
        # 1. Insert login
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO login (username, password, role) VALUES (%s, %s, %s)",
            (username, hashed_password, role)
        )
        login_id = cursor.lastrowid
        
        # 2. Insert employee
        cursor.execute(
            "INSERT INTO employee (name, email, phone, department, designation, login_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, email, phone, department, designation, login_id)
        )
        conn.commit()
        flash('Employee added successfully!', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error adding employee: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('employees'))

@app.route('/employee/edit/<int:id>', methods=['POST'])
@login_required
@roles_required('Admin', 'Manager')
def edit_employee(id):
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    department = request.form.get('department')
    designation = request.form.get('designation')
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    if not name or not email or not username:
        flash('Name, Email and Username are required.', 'danger')
        return redirect(url_for('employees'))
        
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return redirect(url_for('employees'))
        
    cursor = conn.cursor(dictionary=True)
    
    # Check email duplicate (except this employee)
    cursor.execute("SELECT employee_id FROM employee WHERE email = %s AND employee_id != %s", (email, id))
    if cursor.fetchone():
        flash('Email already in use by another employee.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('employees'))
        
    # Get associated login_id
    cursor.execute("SELECT login_id FROM employee WHERE employee_id = %s", (id,))
    emp_record = cursor.fetchone()
    if not emp_record:
        flash('Employee not found.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('employees'))
    login_id = emp_record['login_id']
    
    # Check username duplicate
    cursor.execute("SELECT login_id FROM login WHERE username = %s AND login_id != %s", (username, login_id))
    if cursor.fetchone():
        flash('Username already exists.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('employees'))
        
    try:
        # Update Employee
        cursor.execute("""
            UPDATE employee 
            SET name = %s, email = %s, phone = %s, department = %s, designation = %s 
            WHERE employee_id = %s
        """, (name, email, phone, department, designation, id))
        
        # Update Login Details
        if password:
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                UPDATE login 
                SET username = %s, password = %s, role = %s 
                WHERE login_id = %s
            """, (username, hashed_password, role, login_id))
        else:
            cursor.execute("""
                UPDATE login 
                SET username = %s, role = %s 
                WHERE login_id = %s
            """, (username, role, login_id))
            
        conn.commit()
        flash('Employee updated successfully!', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error updating employee: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('employees'))

@app.route('/employee/delete/<int:id>', methods=['POST'])
@login_required
@roles_required('Admin', 'Manager')
def delete_employee(id):
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return redirect(url_for('employees'))
        
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT login_id FROM employee WHERE employee_id = %s", (id,))
    emp = cursor.fetchone()
    
    if not emp:
        flash('Employee not found.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('employees'))
        
    try:
        # Deleting from parent login table will cascade delete employee due to ON DELETE CASCADE
        cursor.execute("DELETE FROM login WHERE login_id = %s", (emp['login_id'],))
        conn.commit()
        flash('Employee and associated login records deleted successfully!', 'success')
    except Error as e:
        conn.rollback()
        flash(f'Error deleting employee: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('employees'))

@app.route('/tasks')
@login_required
def tasks():
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('dashboard'))
        
    cursor = conn.cursor(dictionary=True)
    role = session['role']
    
    # Fetch tasks
    if role in ['Admin', 'Manager']:
        cursor.execute("""
            SELECT t.*, e.name as assignee_name, e.email as assignee_email
            FROM tasks t
            JOIN employee e ON t.assigned_to = e.employee_id
            ORDER BY t.created_at DESC
        """)
        tasks_list = cursor.fetchall()
        
        # Fetch employees list for task dropdowns/forms
        cursor.execute("SELECT employee_id, name FROM employee ORDER BY name")
        employees_list = cursor.fetchall()
    else:
        emp_id = session.get('employee_id', 0)
        cursor.execute("""
            SELECT t.*, e.name as assignee_name, e.email as assignee_email
            FROM tasks t
            JOIN employee e ON t.assigned_to = e.employee_id
            WHERE t.assigned_to = %s
            ORDER BY t.created_at DESC
        """, (emp_id,))
        tasks_list = cursor.fetchall()
        employees_list = []
        
    cursor.close()
    conn.close()
    
    return render_template('tasks.html', tasks=tasks_list, employees=employees_list)

@app.route('/task/add', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Manager')
def add_task():
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('tasks'))
        
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        assigned_to = request.form.get('assigned_to')
        priority = request.form.get('priority')
        status = request.form.get('status', 'Pending')
        due_date = request.form.get('due_date')
        
        if not title or not assigned_to or not due_date:
            flash('Title, assignee and due date are required.', 'danger')
            cursor.execute("SELECT employee_id, name FROM employee ORDER BY name")
            employees_list = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('add_task.html', employees=employees_list)
            
        try:
            cursor.execute("""
                INSERT INTO tasks (title, description, assigned_to, priority, status, due_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, description, assigned_to, priority, status, due_date))
            conn.commit()
            flash('Task created successfully!', 'success')
            return redirect(url_for('tasks'))
        except Error as e:
            flash(f'Error creating task: {e}', 'danger')
            
    cursor.execute("SELECT employee_id, name FROM employee ORDER BY name")
    employees_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('add_task.html', employees=employees_list, task=None)

@app.route('/task/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Manager')
def edit_task(id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('tasks'))
        
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        assigned_to = request.form.get('assigned_to')
        priority = request.form.get('priority')
        status = request.form.get('status')
        due_date = request.form.get('due_date')
        
        if not title or not assigned_to or not due_date:
            flash('Title, assignee and due date are required.', 'danger')
        else:
            try:
                cursor.execute("""
                    UPDATE tasks 
                    SET title = %s, description = %s, assigned_to = %s, priority = %s, status = %s, due_date = %s
                    WHERE task_id = %s
                """, (title, description, assigned_to, priority, status, due_date, id))
                conn.commit()
                flash('Task updated successfully!', 'success')
                return redirect(url_for('tasks'))
            except Error as e:
                flash(f'Error updating task: {e}', 'danger')
                
    # GET or validation failure: load task and employees
    cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (id,))
    task = cursor.fetchone()
    if not task:
        flash('Task not found.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('tasks'))
        
    # Format date to YYYY-MM-DD for form date picker compatibility
    if task['due_date'] and isinstance(task['due_date'], datetime):
        task['due_date'] = task['due_date'].strftime('%Y-%m-%d')
    elif task['due_date']:
        # if it's already a date object but not datetime
        task['due_date'] = str(task['due_date'])
        
    cursor.execute("SELECT employee_id, name FROM employee ORDER BY name")
    employees_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('add_task.html', employees=employees_list, task=task)

@app.route('/task/delete/<int:id>', methods=['POST'])
@login_required
@roles_required('Admin', 'Manager')
def delete_task(id):
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return redirect(url_for('tasks'))
        
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM tasks WHERE task_id = %s", (id,))
        conn.commit()
        flash('Task deleted successfully!', 'success')
    except Error as e:
        flash(f'Error deleting task: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('tasks'))

@app.route('/task/update-status/<int:id>', methods=['POST'])
@login_required
def update_task_status(id):
    new_status = request.form.get('status')
    if not new_status or new_status not in ['Pending', 'In Progress', 'Completed']:
        flash('Invalid status value.', 'danger')
        return redirect(url_for('tasks'))
        
    conn = get_db_connection()
    if not conn:
        flash('Database error.', 'danger')
        return redirect(url_for('tasks'))
        
    cursor = conn.cursor(dictionary=True)
    
    # If the user is an Employee, they can only update tasks assigned to them
    if session['role'] == 'Employee':
        emp_id = session.get('employee_id', 0)
        cursor.execute("SELECT assigned_to FROM tasks WHERE task_id = %s", (id,))
        task = cursor.fetchone()
        if not task or task['assigned_to'] != emp_id:
            flash('Access denied. You can only update tasks assigned to you.', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('tasks'))
            
    try:
        cursor.execute("UPDATE tasks SET status = %s WHERE task_id = %s", (new_status, id))
        conn.commit()
        flash('Task status updated successfully!', 'success')
    except Error as e:
        flash(f'Error updating task status: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('tasks'))

if __name__ == '__main__':
    # When executing directly, run with host=0.0.0.0 and port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
