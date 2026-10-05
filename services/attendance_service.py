from database.db_manager import DatabaseManager

class AttendanceService:
    def __init__(self):
        self.db = DatabaseManager()

    def add_attendance(self, date, service_type, men=0, women=0, children=0, notes=""):
        total = int(men) + int(women) + int(children)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO attendance (date, service_type, men_count, women_count, children_count, total_count, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (date, service_type, int(men), int(women), int(children), total, notes))
            conn.commit()

    def update_attendance(self, att_id, date, service_type, men, women, children, notes):
        total = int(men) + int(women) + int(children)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE attendance 
                SET date = ?, service_type = ?, men_count = ?, women_count = ?, children_count = ?, total_count = ?, notes = ?
                WHERE id = ?
            """, (date, service_type, int(men), int(women), int(children), total, notes, att_id))
            conn.commit()

    def delete_attendance(self, att_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attendance WHERE id = ?", (att_id,))
            conn.commit()

    def get_all_attendance(self, search_query=""):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if search_query:
                query = "%" + search_query + "%"
                cursor.execute("""
                    SELECT * FROM attendance 
                    WHERE date LIKE ? OR service_type LIKE ? OR notes LIKE ?
                    ORDER BY id DESC
                """, (query, query, query))
            else:
                cursor.execute("SELECT * FROM attendance ORDER BY id DESC")
            return cursor.fetchall()
