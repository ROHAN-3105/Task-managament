# TaskFlow - Full Stack Task Management System

TaskFlow is a premium, modern, and responsive enterprise **Task Management System** built with **Python Flask**, **MySQL**, **HTML5**, **CSS3**, and **Vanilla JavaScript**. It splits the code into a distinct `backend` and `frontend` folder structure, featuring role-based dashboards, glassmorphic UI design, live database analytics, and direct task update mechanisms.

---

## 🌟 Features

*   **Role-Based Access Control**:
    *   **Admin/Manager**: Complete CRUD operations for employees and tasks, real-time dashboard statistics cards, interactive Chart.js graphs, search, and filtration.
    *   **Employee**: Personal dashboard with status breakdowns, and a dedicated tasks view with quick inline status updates.
*   **Security Patches**: Parameterized SQL queries protecting against SQL Injection, secure session handling, and hashed user passwords.
*   **Premium Interactive UX**: Modern glassmorphism UI card system, dark/light theme switching with persistence, count animations, loading spinners, modal popups, and instant toast alerts.
*   **Dynamic Data Plots**: Dynamic dashboard panels powered by Chart.js mapping task status shares, employee load distribution, and overall completion rate gauges.

---

## 📂 Project Structure

```text
TaskManagementSystem/
│
├── database/
│   └── schema.sql              # MySQL table declarations
│
├── backend/
│   ├── app.py                  # Core Flask server & API routes
│   ├── config.py               # Database and app settings
│   ├── init_db.py              # DB creation, password hashing, & seed data
│   ├── verify_app.py           # Automated routing unit tests
│   └── requirements.txt        # Backend dependencies
│
├── frontend/
│   ├── templates/              # HTML layout and views
│   │   ├── base.html           # Authenticated shell layout
│   │   ├── login.html          # Clean standalone login page
│   │   ├── dashboard.html      # Stats and Chart.js dashboards
│   │   ├── employees.html      # Employee tables & CRUD modals
│   │   ├── tasks.html          # Grid task cards & status update
│   │   └── add_task.html       # Unified task creation/editing form
│   │
│   └── static/                 # Static asset resources
│       ├── css/
│       │   └── style.css       # Main stylesheet (Glassmorphism + Dark Mode)
│       └── js/
│           └── script.js       # Frontend UI animations & controls
│
└── README.md                   # Setup documentation
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure you have the following installed on your machine:
*   [Python 3.8+](https://www.python.org/downloads/)
*   [MySQL Server](https://dev.mysql.com/downloads/installer/)

### 2. Configure Database Details
Open `backend/config.py` and modify the default connection parameters to match your local MySQL settings (if different from default `root` with no password):
```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DB = 'task_management'
MYSQL_PORT = 3306
```

### 3. Install Dependencies
Open your command terminal, navigate to the project directory, and execute:
```bash
pip install -r backend/requirements.txt
```

### 4. Initialize Database & Populate Seed Data
Run the database setup script. This script automatically reads `database/schema.sql`, creates the `task_management` database, hashes user passwords, and creates sample records:
```bash
python backend/init_db.py
```

### 5. Run the Server
Launch the Flask development server:
```bash
python backend/app.py
```
Open your browser and navigate to: `http://localhost:5000`

---

## 🔐 Sample Login Credentials

For testing purposes, the initialization script sets up the following users:

| Username | Default Password | Role | Associated Employee Details |
| :--- | :--- | :--- | :--- |
| **admin** | `admin123` | **Admin** | System Superuser |
| **manager** | `manager123` | **Manager** | Team Supervisor |
| **sarah** | `sarah123` | **Employee** | Sarah Chen (Engineering) |
| **james** | `james123` | **Employee** | James Wilson (Marketing) |
| **emily** | `emily123` | **Employee** | Emily Rodriguez (Design) |
| **michael** | `michael123` | **Employee** | Michael Brown (Sales) |
| **priya** | `priya123` | **Employee** | Priya Sharma (HR) |

---

## 🛰️ API Routes Overview

| Route | Method | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Public | Direct redirect helper to login page |
| `/login` | `GET/POST` | Public | Credentials role validation and session storage |
| `/logout` | `GET` | Authenticated | Destroys current session and redirects to login |
| `/dashboard` | `GET` | Authenticated | Displays metric cards and statistics charts |
| `/employees` | `GET` | Admin, Manager | Lists employees directory in a table |
| `/employee/add` | `POST` | Admin, Manager | Appends login and employee records |
| `/employee/edit/<id>` | `POST` | Admin, Manager | Updates existing details / password hashes |
| `/employee/delete/<id>` | `POST` | Admin, Manager | Cascades deletes logins and profiles |
| `/tasks` | `GET` | Authenticated | Lists tasks grid (filtered by owner for Employees) |
| `/task/add` | `GET/POST` | Admin, Manager | Assigns and creates a new task |
| `/task/edit/<id>` | `GET/POST` | Admin, Manager | Updates title, desc, assignee, priority, due date |
| `/task/delete/<id>` | `POST` | Admin, Manager | Deletes task record |
| `/task/update-status/<id>`| `POST` | Assignee, Admin, Manager | Updates task status value instantly |

---
## 🔒 Security

- Password hashing
- Parameterized SQL queries
- Session-based authentication
- Role-based access control
---
## 🧪 Verification Test
You can verify the routing logic and auth protections using the automated script:
```bash
python backend/verify_app.py
```


---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve TaskFlow, please follow these steps:

1. Fork the repository.
2. Create a new feature branch.
3. Make your changes.
4. Commit your changes following the commit message guidelines below.
5. Push your branch and create a Pull Request.

---

## 📝 Commit Message Guidelines

Please use clear and meaningful commit messages.

### Format

```text
<type>: <short description>
```

### Common Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Formatting, UI, CSS changes |
| `refactor` | Code restructuring without changing functionality |
| `perf` | Performance improvements |
| `test` | Adding or updating tests |
| `chore` | Build process, dependencies, miscellaneous updates |

### Examples

```bash
feat: add employee dashboard analytics
fix: resolve task status update issue
docs: update installation guide
style: improve login page responsiveness
refactor: optimize database connection handling
perf: reduce dashboard loading time
test: add authentication route tests
chore: update project dependencies
```

---

## 📌 Git Workflow

```bash
# Clone repository
git clone <repository-url>

# Create a new branch
git checkout -b feature/your-feature-name

# Stage changes
git add .

# Commit changes
git commit -m "feat: add task priority filter"

# Push changes
git push origin feature/your-feature-name
```

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub. It helps others discover the project and motivates future improvements.
