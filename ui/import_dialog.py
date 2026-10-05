import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QComboBox, QTableWidget, QTableWidgetItem, 
    QMessageBox, QGroupBox, QHeaderView, QTextEdit
)
from PyQt6.QtCore import Qt
from utils.importer import BulkMemberImporter

class BulkImportDialog(QDialog):
    DB_FIELDS = {
        'full_name': 'Full Name *',
        'gender': 'Gender *',
        'phone_number': 'Phone Number',
        'email': 'Email',
        'dob': 'Date of Birth (YYYY-MM-DD)',
        'address': 'Address / Location',
        'group_name': 'Generational Group / Guild',
        'status': 'Membership Status'
    }

    def __init__(self, db_path="church.db", parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.importer = BulkMemberImporter(db_path=db_path)
        self.file_headers = []
        self.raw_records = []
        self.mapping_combos = {}

        self.setWindowTitle("Bulk Import Members (CSV / Excel)")
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # File Selector Group
        file_group = QGroupBox("1. Select Member Roster File")
        file_layout = QHBoxLayout(file_group)
        
        self.btn_select_file = QPushButton("Browse Excel / CSV File...")
        self.btn_select_file.clicked.connect(self.handle_browse_file)
        self.lbl_file_path = QLabel("No file selected.")
        self.lbl_file_path.setStyleSheet("color: #7f8c8d; font-style: italic;")

        file_layout.addWidget(self.btn_select_file)
        file_layout.addWidget(self.lbl_file_path, stretch=1)
        layout.addWidget(file_group)

        # Column Mapping Group
        self.mapping_group = QGroupBox("2. Map File Columns to Database Fields")
        self.mapping_layout = QVBoxLayout(self.mapping_group)
        layout.addWidget(self.mapping_group)

        # Preview Table
        preview_group = QGroupBox("3. Data Preview (First 5 Rows)")
        preview_layout = QVBoxLayout(preview_group)
        self.table_preview = QTableWidget()
        preview_layout.addWidget(self.table_preview)
        layout.addWidget(preview_group)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_import = QPushButton("Execute Bulk Import")
        self.btn_import.setEnabled(False)
        self.btn_import.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
        self.btn_import.clicked.connect(self.handle_execute_import)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_import)
        layout.addLayout(btn_layout)

    def handle_browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Member Roster", "", "Excel / CSV Files (*.xlsx *.xls *.csv)"
        )
        if not file_path:
            return

        try:
            self.file_headers, self.raw_records = self.importer.read_file(file_path)
            self.lbl_file_path.setText(os.path.basename(file_path))
            self.lbl_file_path.setStyleSheet("color: #2c3e50; font-weight: bold;")

            self.setup_mapping_controls()
            self.populate_preview_table()
            self.btn_import.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "File Read Error", f"Could not read file: {e}")

    def setup_mapping_controls(self):
        # Clear previous widgets in layout
        for i in reversed(range(self.mapping_layout.count())):
            widget = self.mapping_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.mapping_combos.clear()
        
        headers_with_none = ["-- Skip Field --"] + self.file_headers

        for db_key, display_name in self.DB_FIELDS.items():
            row_layout = QHBoxLayout()
            lbl = QLabel(f"<b>{display_name}:</b>")
            lbl.setFixedWidth(220)
            
            combo = QComboBox()
            combo.addItems(headers_with_none)

            # Auto-detect best column match by name
            for header in self.file_headers:
                if db_key.replace('_', '') in header.lower().replace(' ', '').replace('_', ''):
                    combo.setCurrentText(header)
                    break
                elif db_key == 'full_name' and ('name' in header.lower() or 'member' in header.lower()):
                    combo.setCurrentText(header)
                    break

            row_layout.addWidget(lbl)
            row_layout.addWidget(combo, stretch=1)
            self.mapping_layout.addLayout(row_layout)
            self.mapping_combos[db_key] = combo

    def populate_preview_table(self):
        self.table_preview.clear()
        preview_rows = self.raw_records[:5]
        
        self.table_preview.setRowCount(len(preview_rows))
        self.table_preview.setColumnCount(len(self.file_headers))
        self.table_preview.setHorizontalHeaderLabels(self.file_headers)

        for row_idx, record in enumerate(preview_rows):
            for col_idx, header in enumerate(self.file_headers):
                val = str(record.get(header, ''))
                self.table_preview.setItem(row_idx, col_idx, QTableWidgetItem(val))

    def handle_execute_import(self):
        column_mapping = {}
        for db_key, combo in self.mapping_combos.items():
            selected = combo.currentText()
            if selected != "-- Skip Field --":
                column_mapping[db_key] = selected

        if 'full_name' not in column_mapping:
            QMessageBox.warning(self, "Mapping Incomplete", "Please map at least the 'Full Name' field.")
            return

        try:
            count, errors = self.importer.import_members(self.raw_records, column_mapping)
            
            msg = f"Successfully imported {count} members into the database!"
            if errors:
                msg += f"\n\nSkipped / Warnings ({len(errors)}):\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    msg += f"\n...and {len(errors) - 5} more issues."

            QMessageBox.information(self, "Import Complete", msg)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"An error occurred during import:\n{e}")
