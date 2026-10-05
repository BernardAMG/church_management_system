from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QDateEdit, QTableWidget, QTableWidgetItem, QPushButton, 
    QMessageBox, QHeaderView, QGroupBox
)
from PyQt6.QtCore import QDate

class RollCallDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Mark Service Attendance / Roll Call")
        self.resize(650, 500)
        self.status_combos = {}  # {member_name: QComboBox}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header Info Group
        config_group = QGroupBox("Service Details")
        config_layout = QHBoxLayout(config_group)

        config_layout.addWidget(QLabel("Service:"))
        self.cb_service = QComboBox()
        self.cb_service.addItems(["Sunday Morning Service", "Midweek Prayer", "Youth Service", "Special Event"])
        config_layout.addWidget(self.cb_service)

        config_layout.addWidget(QLabel("Date:"))
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        config_layout.addWidget(self.date_picker)

        layout.addWidget(config_group)

        # Roll Call Table Setup
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Member Name", "Member Status", "Attendance Marker"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.load_members()

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_mark_all_present = QPushButton("Mark All Present")
        self.btn_mark_all_present.clicked.connect(self.mark_all_present)

        self.btn_save = QPushButton("Save Attendance")
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_attendance)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_mark_all_present)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def load_members(self):
        if not self.db:
            return

        members = self.db.get_all_members()
        self.table.setRowCount(len(members))

        for row, member in enumerate(members):
            # member tuple structure: (id, name, phone, email, gender, status)
            name = member[1]
            member_status = member[5]

            # Column 0: Name
            self.table.setItem(row, 0, QTableWidgetItem(name))

            # Column 1: Member Category Status
            self.table.setItem(row, 1, QTableWidgetItem(member_status))

            # Column 2: Interactive Attendance Selector
            combo = QComboBox()
            combo.addItems(["Present", "Absent", "Excused"])
            combo.setCurrentText("Present")
            self.status_combos[name] = combo
            self.table.setCellWidget(row, 2, combo)

    def mark_all_present(self):
        for combo in self.status_combos.values():
            combo.setCurrentText("Present")

    def save_attendance(self):
        service = self.cb_service.currentText()
        date_str = self.date_picker.date().toString("yyyy-MM-dd")

        records = []
        for name, combo in self.status_combos.items():
            records.append((name, service, date_str, combo.currentText()))

        try:
            if self.db:
                self.db.add_bulk_attendance(records)
            QMessageBox.information(self, "Success", f"Attendance successfully saved for {len(records)} members!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save roll call: {e}")
