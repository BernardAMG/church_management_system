from database.db_manager import DatabaseManager

class FinanceService:
    def __init__(self):
        self.db = DatabaseManager()

    def add_transaction(self, date, trans_type, category, amount, description=""):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (date, type, category, amount, description)
                VALUES (?, ?, ?, ?, ?)
            """, (date, trans_type, category, float(amount), description))
            conn.commit()

    def update_transaction(self, trans_id, date, trans_type, category, amount, description):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions 
                SET date = ?, type = ?, category = ?, amount = ?, description = ?
                WHERE id = ?
            """, (date, trans_type, category, float(amount), description, trans_id))
            conn.commit()

    def delete_transaction(self, trans_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
            conn.commit()

    def get_all_transactions(self, search_query=""):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if search_query:
                query = "%" + search_query + "%"
                cursor.execute("""
                    SELECT * FROM transactions 
                    WHERE date LIKE ? OR type LIKE ? OR category LIKE ? OR description LIKE ?
                    ORDER BY id DESC
                """, (query, query, query, query))
            else:
                cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
            return cursor.fetchall()

    def get_financial_summary(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) as total_expense
                FROM transactions
            """)
            row = cursor.fetchone()
            income = row['total_income'] or 0.0
            expense = row['total_expense'] or 0.0
            balance = income - expense
            return income, expense, balance
