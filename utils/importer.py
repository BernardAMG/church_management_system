import sqlite3
import pandas as pd

class BulkMemberImporter:
    REQUIRED_FIELDS = ['full_name', 'gender']
    ALLOWED_FIELDS = [
        'full_name', 'gender', 'phone_number', 'email', 
        'dob', 'address', 'group_name', 'status'
    ]

    def __init__(self, db_path="church.db"):
        self.db_path = db_path

    def read_file(self, file_path):
        """Reads CSV or Excel file and returns headers and data rows."""
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, dtype=str)
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path, dtype=str)
        else:
            raise ValueError("Unsupported file format. Please upload a .csv, .xls, or .xlsx file.")
        
        # Clean missing values to empty strings
        df = df.fillna('')
        return list(df.columns), df.to_dict(orient='records')

    def import_members(self, records, column_mapping):
        """
        Imports mapped records into the database inside a single transaction.
        column_mapping: dict mapping DB field -> File column name
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        errors = []

        try:
            conn.execute("BEGIN TRANSACTION")

            for index, row in enumerate(records, start=1):
                full_name = row.get(column_mapping.get('full_name', ''), '').strip()
                gender = row.get(column_mapping.get('gender', ''), '').strip()

                if not full_name:
                    errors.append(f"Row {index}: Missing required field 'Full Name'. Skipped.")
                    continue

                gender = gender.capitalize() if gender else 'Unspecified'
                phone = row.get(column_mapping.get('phone_number', ''), '').strip()
                email = row.get(column_mapping.get('email', ''), '').strip()
                dob = row.get(column_mapping.get('dob', ''), '').strip()
                address = row.get(column_mapping.get('address', ''), '').strip()
                group_name = row.get(column_mapping.get('group_name', ''), '').strip() or 'General'
                status = row.get(column_mapping.get('status', ''), '').strip() or 'Active'

                cursor.execute("""
                    INSERT INTO members (full_name, gender, phone_number, email, dob, address, group_name, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (full_name, gender, phone, email, dob, address, group_name, status))

                imported_count += 1

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Database insertion failed: {e}")
        finally:
            conn.close()

        return imported_count, errors
