import hashlib
from database.db_manager import DatabaseManager

class AuthService:
    def __init__(self):
        self.db = DatabaseManager()
        self.init_auth_table()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def init_auth_table(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            ''')
            conn.commit()

            cursor.execute('SELECT COUNT(*) as count FROM users')
            if cursor.fetchone()['count'] == 0:
                admin_hash = self._hash_password('admin123')
                treasurer_hash = self._hash_password('treasurer123')
                secretary_hash = self._hash_password('secretary123')
                
                cursor.executemany('''
                    INSERT INTO users (username, password_hash, role)
                    VALUES (?, ?, ?)
                ''', [
                    ('admin', admin_hash, 'Admin'),
                    ('treasurer', treasurer_hash, 'Treasurer'),
                    ('secretary', secretary_hash, 'Secretary')
                ])
                conn.commit()

    def authenticate(self, username, password):
        password_hash = self._hash_password(password)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, role FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            return cursor.fetchone()
