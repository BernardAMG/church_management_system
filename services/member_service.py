from database.db_manager import DatabaseManager

class MemberService:
    def __init__(self):
        self.db = DatabaseManager()

    def add_member(self, full_name, phone="", email="", address="", gender="Other", status="Active", joined_date=""):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO members (full_name, phone, email, address, gender, status, joined_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (full_name, phone, email, address, gender, status, joined_date))
            conn.commit()

    def update_member(self, member_id, full_name, phone, email, address):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE members 
                SET full_name = ?, phone = ?, email = ?, address = ?
                WHERE id = ?
            """, (full_name, phone, email, address, member_id))
            conn.commit()

    def delete_member(self, member_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
            conn.commit()

    def get_all_members(self, search_query=""):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if search_query:
                query = "%" + search_query + "%"
                cursor.execute("""
                    SELECT * FROM members 
                    WHERE full_name LIKE ? OR phone LIKE ? OR email LIKE ? OR address LIKE ?
                    ORDER BY id DESC
                """, (query, query, query, query))
            else:
                cursor.execute("SELECT * FROM members ORDER BY id DESC")
            return cursor.fetchall()
