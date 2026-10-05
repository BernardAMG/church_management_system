import sqlite3
import hashlib
import os

class DatabaseManager:
    def __init__(self, db_name="church.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def hash_password(password, salt=None):
        if not salt:
            salt = os.urandom(16)
        else:
            if isinstance(salt, str):
                salt = bytes.fromhex(salt)
        
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return pwd_hash.hex(), salt.hex()

    @staticmethod
    def verify_password(stored_hash, stored_salt, provided_password):
        salt_bytes = bytes.fromhex(stored_salt)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt_bytes,
            100000
        )
        return pwd_hash.hex() == stored_hash

    def log_audit(self, user_id, action, details=""):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO audit_logs (user_id, action, details)
                    VALUES (?, ?, ?)
                ''', (user_id, action, details))
                conn.commit()
        except Exception as e:
            print(f"Error logging audit trail: {e}")

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    gender TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    membership_status TEXT DEFAULT 'Active',
                    date_joined TEXT
                )
            ''')

            # Financials table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trans_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    member_id INTEGER,
                    description TEXT,
                    trans_date TEXT DEFAULT (DATE('now')),
                    FOREIGN KEY (member_id) REFERENCES members(id)
                )
            ''')

            # Attendance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_date TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    member_id INTEGER,
                    status TEXT DEFAULT 'Present',
                    remarks TEXT,
                    FOREIGN KEY (member_id) REFERENCES members(id)
                )
            ''')

            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'Viewer',
                    status TEXT DEFAULT 'Active',
                    created_at TEXT DEFAULT (DATETIME('now'))
                )
            ''')

            # Audit Logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT DEFAULT (DATETIME('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # Insert default Admin and standard accounts if empty
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                default_users = [
                    ('admin', 'admin123', 'System Administrator', 'Admin'),
                    ('secretary', 'sec123', 'Church Secretary', 'Secretary'),
                    ('treasurer', 'pay123', 'Head Treasurer', 'Treasurer'),
                    ('viewer', 'view123', 'Guest Viewer', 'Viewer')
                ]
                for u_name, pwd, f_name, u_role in default_users:
                    p_hash, p_salt = self.hash_password(pwd)
                    cursor.execute('''
                        INSERT INTO users (username, password_hash, salt, full_name, role)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (u_name, p_hash, p_salt, f_name, u_role))

            conn.commit()
