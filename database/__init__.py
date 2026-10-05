import sqlite3
import os
from utils.security import SecurityUtils

class DatabaseManager:
    def __init__(self, db_path="church_cms.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    email TEXT,
                    gender TEXT,
                    status TEXT DEFAULT 'Active'
                )
            ''')

            # Attendance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_name TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    date_str TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            ''')

            # Financials table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS finances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trans_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date_str TEXT NOT NULL,
                    member_name TEXT,
                    notes TEXT
                )
            ''')

            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            ''')

            # Seed default admin user if users table is empty
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                pwd_hash, salt = SecurityUtils.hash_password("admin123")
                cursor.execute(
                    "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
                    ("admin", pwd_hash, salt, "Main Admin")
                )

            # Seed default data if members table is empty
            cursor.execute("SELECT COUNT(*) FROM members")
            if cursor.fetchone()[0] == 0:
                default_members = [
                    ("John Doe", "0241234567", "john@example.com", "Male", "Active"),
                    ("Jane Smith", "0209876543", "jane@example.com", "Female", "Active"),
                    ("Kofi Mensah", "0551122334", "kofi@example.com", "Male", "Inactive"),
                    ("Ama Serwaa", "0275566778", "ama@example.com", "Female", "Visitor")
                ]
                cursor.executemany(
                    "INSERT INTO members (name, phone, email, gender, status) VALUES (?, ?, ?, ?, ?)",
                    default_members
                )

            # Seed default data if attendance table is empty
            cursor.execute("SELECT COUNT(*) FROM attendance")
            if cursor.fetchone()[0] == 0:
                default_attendance = [
                    ("John Doe", "Sunday Morning Service", "2026-10-04", "Present"),
                    ("Jane Smith", "Sunday Morning Service", "2026-10-04", "Present"),
                    ("Kofi Mensah", "Sunday Morning Service", "2026-10-04", "Absent"),
                    ("Ama Serwaa", "Midweek Prayer", "2026-10-01", "Present"),
                    ("John Doe", "Midweek Prayer", "2026-10-01", "Excused"),
                    ("Jane Smith", "Youth Service", "2026-09-27", "Present"),
                ]
                cursor.executemany(
                    "INSERT INTO attendance (member_name, service_type, date_str, status) VALUES (?, ?, ?, ?)",
                    default_attendance
                )

            # Seed default data if finances table is empty
            cursor.execute("SELECT COUNT(*) FROM finances")
            if cursor.fetchone()[0] == 0:
                default_finances = [
                    ("Income", "Tithe", 500.00, "2026-10-04", "John Doe", "October Tithe"),
                    ("Income", "Offering", 1200.50, "2026-10-04", "General", "Sunday Offering"),
                    ("Income", "Donation", 300.00, "2026-10-02", "Jane Smith", "Building Fund"),
                    ("Expense", "Utilities", 450.00, "2026-10-03", "ECG Electricity", "Monthly Bill"),
                    ("Expense", "Maintenance", 200.00, "2026-09-30", "Vendor", "PA System Repair"),
                ]
                cursor.executemany(
                    "INSERT INTO finances (trans_type, category, amount, date_str, member_name, notes) VALUES (?, ?, ?, ?, ?, ?)",
                    default_finances
                )

            conn.commit()

    # --- USER AUTHENTICATION & MANAGEMENT METHODS ---
    def authenticate_user(self, username, password):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash, salt, role FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if not user:
                return None
                
            user_id, uname, stored_hash, stored_salt, role = user
            if SecurityUtils.verify_password(stored_hash, stored_salt, password):
                return {"id": user_id, "username": uname, "role": role}
            return None

    def add_user(self, username, password, role):
        pwd_hash, salt = SecurityUtils.hash_password(password)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
                (username, pwd_hash, salt, role)
            )
            conn.commit()

    def update_user(self, user_id, username, password, role):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if password:
                pwd_hash, salt = SecurityUtils.hash_password(password)
                cursor.execute(
                    "UPDATE users SET username = ?, password_hash = ?, salt = ?, role = ? WHERE id = ?",
                    (username, pwd_hash, salt, role, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET username = ?, role = ? WHERE id = ?",
                    (username, role, user_id)
                )
            conn.commit()

    def get_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM users ORDER BY id ASC")
            return cursor.fetchall()

    def delete_user(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()

    # --- MEMBERS METHODS ---
    def get_all_members(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, phone, email, gender, status FROM members ORDER BY id DESC")
            return cursor.fetchall()

    def add_member(self, name, phone, email, gender, status):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO members (name, phone, email, gender, status) VALUES (?, ?, ?, ?, ?)",
                (name, phone, email, gender, status)
            )
            conn.commit()

    def update_member(self, original_phone, name, phone, email, gender, status):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE members SET name=?, phone=?, email=?, gender=?, status=? WHERE phone=?",
                (name, phone, email, gender, status, original_phone)
            )
            conn.commit()

    # --- ATTENDANCE METHODS ---
    def get_attendance(self, service_type=None, year=None, month_num=None, date_str=None):
        query = "SELECT member_name, service_type, date_str, status FROM attendance WHERE 1=1"
        params = []

        if service_type and service_type != "All Services":
            query += " AND service_type = ?"
            params.append(service_type)

        if year and year != "All Years":
            query += " AND strftime('%Y', date_str) = ?"
            params.append(year)

        if month_num and month_num != "All Months":
            query += " AND strftime('%m', date_str) = ?"
            params.append(month_num)

        if date_str and date_str != "All Dates":
            query += " AND date_str = ?"
            params.append(date_str)

        query += " ORDER BY date_str DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def add_attendance_record(self, member_name, service_type, date_str, status):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO attendance (member_name, service_type, date_str, status) VALUES (?, ?, ?, ?)",
                (member_name, service_type, date_str, status)
            )
            conn.commit()

    def add_bulk_attendance(self, records):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO attendance (member_name, service_type, date_str, status) VALUES (?, ?, ?, ?)",
                records
            )
            conn.commit()

    # --- FINANCIALS METHODS ---
    def get_finances(self, trans_type=None, category=None):
        query = "SELECT trans_type, category, amount, date_str, member_name, notes FROM finances WHERE 1=1"
        params = []

        if trans_type and trans_type != "All Types":
            query += " AND trans_type = ?"
            params.append(trans_type)

        if category and category != "All Categories":
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY date_str DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def add_financial_record(self, trans_type, category, amount, date_str, member_name="", notes=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO finances (trans_type, category, amount, date_str, member_name, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (trans_type, category, amount, date_str, member_name, notes)
            )
            conn.commit()

    # --- DASHBOARD METHODS ---
    def get_dashboard_summary(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM members WHERE status = 'Active'")
            active_members = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM members")
            total_members = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(amount) FROM finances WHERE trans_type = 'Income'")
            total_income = cursor.fetchone()[0] or 0.0

            cursor.execute("SELECT SUM(amount) FROM finances WHERE trans_type = 'Expense'")
            total_expense = cursor.fetchone()[0] or 0.0

            cursor.execute("SELECT COUNT(*) FROM attendance WHERE status = 'Present'")
            total_present = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM attendance")
            total_attendance_records = cursor.fetchone()[0]

            avg_attendance_rate = (total_present / total_attendance_records * 100) if total_attendance_records > 0 else 0.0

            return {
                "active_members": active_members,
                "total_members": total_members,
                "total_income": total_income,
                "total_expense": total_expense,
                "net_balance": total_income - total_expense,
                "attendance_rate": avg_attendance_rate
            }
