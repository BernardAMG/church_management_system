import sqlite3
import os

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

            conn.commit()

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
