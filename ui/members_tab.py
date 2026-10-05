from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QComboBox, QLabel, QGroupBox
)
from utils.exporter import DataExporter
from ui.member_dialog import AddMemberDialog

class MembersTab(QWidget):
    def __init__(self, db=None, user_role="Church Admin", parent=None):
        super().__init__(parent)
        self.db = db
        self.user_role = user_role
        self.all_members_cache = []  # Stores full DB dataset for fast in-memory filtering
        self.init_ui()
        self.load_members()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Action Bar (Add, Edit, Export)
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Member")
        self.add_btn.clicked.connect(self.open_add_member_dialog)
        
        self.edit_btn = QPushButton("Edit Selected Member")
        self.edit_btn.clicked.connect(self.edit_selected_member)

        is_admin = self.user_role in ["Main Admin", "Church Admin"]
        self.add_btn.setEnabled(is_admin)
        self.edit_btn.setEnabled(is_admin)

        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)

        self.export_pdf_btn = QPushButton("Export PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.export_csv_btn)
        btn_layout.addWidget(self.export_pdf_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # Search & Filter Controls Group
        filter_group = QGroupBox("Search & Filter Directory")
        filter_layout = QHBoxLayout(filter_group)

        # Search Box Input
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, phone, or email...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.apply_directory_filters)
        filter_layout.addWidget(self.search_input)

        # Status Dropdown Filter
        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Statuses", "Active", "Inactive", "Visitor"])
        self.status_filter.currentTextChanged.connect(self.apply_directory_filters)
        filter_layout.addWidget(self.status_filter)

        # Reset Filters Button
        self.reset_btn = QPushButton("Reset Filters")
        self.reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.reset_btn)

        # Result Counter
        self.lbl_record_count = QLabel("Showing 0 records")
        self.lbl_record_count.setStyleSheet("font-weight: bold; color: #555;")
        filter_layout.addWidget(self.lbl_record_count)

        layout.addWidget(filter_group)

        # Table Setup
        self.table = QTableWidget()
        self.headers = ["Name", "Phone", "Email", "Gender", "Status"]
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.doubleClicked.connect(self.edit_selected_member)
        layout.addWidget(self.table)

    def reset_filters(self):
        """Clears search input and resets status filter to show all rows."""
        self.search_input.blockSignals(True)
        self.status_filter.blockSignals(True)
        
        self.search_input.clear()
        self.status_filter.setCurrentIndex(0)  # "All Statuses"
        
        self.search_input.blockSignals(False)
        self.status_filter.blockSignals(False)
        self.apply_directory_filters()

    def load_members(self):
        """Loads fresh data from SQLite database into memory cache and applies current filters."""
        if not self.db:
            return
        try:
            # Query all members from SQLite
            raw_members = self.db.get_all_members()
            # Convert tuples (id, name, phone, email, gender, status) -> string list
            self.all_members_cache = [
                [str(field) if field is not None else "" for field in m[1:6]]
                for m in raw_members
            ]
            self.apply_directory_filters()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load members: {e}")

    def apply_directory_filters(self):
        """Filters cached members based on search query and selected status in real time."""
        search_query = self.search_input.text().strip().lower()
        selected_status = self.status_filter.currentText()

        filtered_rows = []
        for row in self.all_members_cache:
            name, phone, email, gender, status = row

            # Status Filter Match
            if selected_status != "All Statuses" and status != selected_status:
                continue

            # Real-time Text Search Match (Name, Phone, Email)
            if search_query:
                matches_search = (
                    search_query in name.lower() or
                    search_query in phone.lower() or
                    search_query in email.lower()
                )
                if not matches_search:
                    continue

            filtered_rows.append(row)

        # Populate Table Widget
        self.table.setRowCount(0)
        for row_idx, member in enumerate(filtered_rows):
            self.table.insertRow(row_idx)
            for col_idx, text in enumerate(member):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(text))

        # Update Counter Label
        self.lbl_record_count.setText(f"Showing {len(filtered_rows)} of {len(self.all_members_cache)} members")

    def open_add_member_dialog(self):
        dialog = AddMemberDialog(self)
        if dialog.exec() == AddMemberDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                if self.db:
                    self.db.add_member(*data)
                
                # Auto-reset filters so new member is guaranteed to be visible
                self.reset_filters()
                self.load_members()
                QMessageBox.information(self, "Success", "Member added successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Could not save member: {e}")

    def edit_selected_member(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.information(self, "Select Member", "Please click on a member row to edit.")
            return

        current_data = [
            self.table.item(selected_row, col).text() if self.table.item(selected_row, col) else ""
            for col in range(self.table.columnCount())
        ]

        dialog = AddMemberDialog(self, member_data=current_data)
        if dialog.exec() == AddMemberDialog.DialogCode.Accepted:
            updated_data = dialog.get_data()
            try:
                if self.db:
                    original_phone = current_data[1]
                    self.db.update_member(original_phone, *updated_data)
                self.load_members()
                QMessageBox.information(self, "Success", "Member record updated successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Could not update member: {e}")

    def get_table_data(self):
        rows = []
        for row in range(self.table.rowCount()):
            row_data = [self.table.item(row, col).text() if self.table.item(row, col) else "" for col in range(self.table.columnCount())]
            rows.append(row_data)
        return rows

    def export_csv(self):
        rows = self.get_table_data()
        DataExporter.export_to_csv(self, self.headers, rows, "filtered_members_list.csv")

    def export_pdf(self):
        rows = self.get_table_data()
        DataExporter.export_to_pdf(self, "Church Members Directory", self.headers, rows, "filtered_members_list.pdf")
