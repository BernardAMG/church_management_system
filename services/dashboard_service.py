from database.db_manager import DatabaseManager

class DashboardService:
    def __init__(self):
        self.db = DatabaseManager()

    def get_summary_metrics(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as total FROM members")
            total_members = cursor.fetchone()["total"] or 0

            cursor.execute("SELECT SUM(amount) as total FROM transactions WHERE type='Income'")
            total_income = cursor.fetchone()["total"] or 0.0

            cursor.execute("SELECT SUM(amount) as total FROM transactions WHERE type='Expense'")
            total_expense = cursor.fetchone()["total"] or 0.0

            cursor.execute("SELECT SUM(men_count + women_count + children_count) as total FROM attendance")
            total_attendance = cursor.fetchone()["total"] or 0

            return {
                "total_members": total_members,
                "net_balance": total_income - total_expense,
                "total_income": total_income,
                "total_attendance": total_attendance
            }

    def get_monthly_financials(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m', date) as month,
                    SUM(CASE WHEN type='Income' THEN amount ELSE 0 END) as income,
                    SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END) as expense
                FROM transactions
                WHERE date IS NOT NULL AND date != ''
                GROUP BY month
                ORDER BY month ASC
                LIMIT 6
            """)
            return cursor.fetchall()

    def get_attendance_breakdown(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    SUM(men_count) as men,
                    SUM(women_count) as women,
                    SUM(children_count) as children
                FROM attendance
            """)
            row = cursor.fetchone()
            return {
                "Men": row["men"] or 0,
                "Women": row["women"] or 0,
                "Children": row["children"] or 0
            }
