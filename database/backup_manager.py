import os
import sqlite3
import shutil
import datetime

class BackupManager:
    def __init__(self, db_path="church.db", backup_dir="backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, custom_label="manual"):
        """Creates an atomic SQLite backup with timestamping."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file '{self.db_path}' not found.")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"church_backup_{timestamp}_{custom_label}.db"
        backup_filepath = os.path.join(self.backup_dir, backup_filename)

        # Use SQLite Online Backup API for hot backup
        src_conn = sqlite3.connect(self.db_path)
        dst_conn = sqlite3.connect(backup_filepath)

        with dst_conn:
            src_conn.backup(dst_conn)

        dst_conn.close()
        src_conn.close()

        return backup_filepath

    def restore_backup(self, backup_filepath):
        """Restores database from selected backup file after safety check."""
        if not os.path.exists(backup_filepath):
            raise FileNotFoundError(f"Backup file '{backup_filepath}' does not exist.")

        # Create safety snapshot of current state before overwrite
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safety_file = os.path.join(self.backup_dir, f"pre_restore_safety_{timestamp}.db")

        if os.path.exists(self.db_path):
            shutil.copy2(self.db_path, safety_file)

        # Restore from target backup
        src_conn = sqlite3.connect(backup_filepath)
        dst_conn = sqlite3.connect(self.db_path)

        with dst_conn:
            src_conn.backup(dst_conn)

        dst_conn.close()
        src_conn.close()

        return safety_file

    def list_backups(self):
        """Returns sorted list of backup files with metadata."""
        if not os.path.exists(self.backup_dir):
            return []

        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith(".db"):
                path = os.path.join(self.backup_dir, file)
                stats = os.stat(path)
                size_kb = round(stats.st_size / 1024, 2)
                created_at = datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                backups.append({
                    "filename": file,
                    "path": path,
                    "size": f"{size_kb} KB",
                    "date": created_at
                })

        # Sort newest first
        return sorted(backups, key=lambda x: x['date'], reverse=True)
