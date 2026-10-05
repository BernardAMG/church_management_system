import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QGroupBox, 
    QMessageBox, QFileDialog, QHeaderView
)
from PyQt6.QtCore import Qt
from database.backup_manager import BackupManager

class BackupRestoreTab(QWidget):
    def __init__(self, db_path="church.db", current_user="admin"):
        super().__init__()
        self.backup_manager = BackupManager(db_path=db_path)
        self.current_user = current_user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Section 1: Create Backup Controls
        create_group = QGroupBox("Create New Backup")
        create_layout = QHBoxLayout(create_group)
        
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Optional label (e.g., pre_update, monthly_close)")
        
        btn_create = QPushButton("Create Immediate Backup")
        btn_create.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 6px;")
        btn_create.clicked.connect(self.handle_create_backup)
        
        create_layout.addWidget(QLabel("Label:"))
        create_layout.addWidget(self.label_input)
        create_layout.addWidget(btn_create)
        layout.addWidget(create_group)

        # Section 2: Backup History Table
        table_group = QGroupBox("Available Backups")
        table_layout = QVBoxLayout(table_group)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Filename", "Created Date", "File Size"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_group)

        # Section 3: Restore & Management Actions
        action_layout = QHBoxLayout()
        
        btn_refresh = QPushButton("Refresh List")
        btn_refresh.clicked.connect(self.load_backups)
        
        btn_restore_selected = QPushButton("Restore Selected Backup")
        btn_restore_selected.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold; padding: 6px;")
        btn_restore_selected.clicked.connect(self.handle_restore_selected)
        
        btn_import_external = QPushButton("Import & Restore External .db...")
        btn_import_external.clicked.connect(self.handle_restore_external)
        
        action_layout.addWidget(btn_refresh)
        action_layout.addStretch()
        action_layout.addWidget(btn_import_external)
        action_layout.addWidget(btn_restore_selected)
        
        layout.addLayout(action_layout)

        # Load initial list
        self.load_backups()

    def load_backups(self):
        """Populates the table with available backup snapshots."""
        backups = self.backup_manager.list_backups()
        self.table.setRowCount(len(backups))
        
        for row, item in enumerate(backups):
            file_item = QTableWidgetItem(item['filename'])
            file_item.setData(Qt.ItemDataRole.UserRole, item['path'])
            
            self.table.setItem(row, 0, file_item)
            self.table.setItem(row, 1, QTableWidgetItem(item['date']))
            self.table.setItem(row, 2, QTableWidgetItem(item['size']))

    def handle_create_backup(self):
        label = self.label_input.text().strip() or "manual"
        try:
            path = self.backup_manager.create_backup(custom_label=label)
            QMessageBox.information(
                self, 
                "Backup Created", 
                f"Database backup saved successfully:\n{os.path.basename(path)}"
            )
            self.label_input.clear()
            self.load_backups()
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to create backup: {e}")

    def handle_restore_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a backup file from the table.")
            return

        row = selected_rows[0].row()
        backup_path = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        filename = self.table.item(row, 0).text()

        confirm = QMessageBox.warning(
            self,
            "Confirm Restore",
            f"Are you sure you want to restore '{filename}'?\n\n"
            "Current database state will be replaced. A safety snapshot will be created automatically prior to restore.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                safety_path = self.backup_manager.restore_backup(backup_path)
                QMessageBox.information(
                    self, 
                    "Restore Successful", 
                    f"Database restored successfully!\n\nSafety snapshot created at:\n{os.path.basename(safety_path)}"
                )
                self.load_backups()
            except Exception as e:
                QMessageBox.critical(self, "Restore Error", f"Failed to restore database: {e}")

    def handle_restore_external(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select External Database File", "", "SQLite Database (*.db *.sqlite)"
        )
        if not file_path:
            return

        confirm = QMessageBox.warning(
            self,
            "Confirm External Restore",
            f"Restore system from external file:\n{file_path}?\n\n"
            "A safety snapshot of the current state will be created.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                safety_path = self.backup_manager.restore_backup(file_path)
                QMessageBox.information(
                    self, 
                    "Restore Successful", 
                    f"Database restored from external file!\n\nSafety snapshot created at:\n{os.path.basename(safety_path)}"
                )
                self.load_backups()
            except Exception as e:
                QMessageBox.critical(self, "Restore Error", f"Failed to restore external file: {e}")
