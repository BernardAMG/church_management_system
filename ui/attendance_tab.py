from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
    QComboBox, QLabel, QGroupBox
)
from utils.exporter import DataExporter
from ui.roll_call_dialog import RollCallDialog

class AttendanceTab(QWidget):
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
        self.populate_filters()
        self.load_attendance()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Actions & Filter Bar
        action_layout = QHBoxLayout()

        self.btn_take_attendance = QPushButton("Take Roll Call")
        self.btn_take_attendance.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold;")
        self.btn_take_attendance.clicked.connect(self.open_roll_call_dialog)

        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)

        self.export_pdf_btn = QPushButton("Export PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)

        action_layout.addWidget(self.btn_take_attendance)
        action_layout.addWidget(self.export_csv_btn)
        action_layout.addWidget(self.export_pdf_btn)
        action_layout.addStretch()

        layout.addLayout(action_layout)

        # Filters Group
        filter_group = QGroupBox("Filter Records")
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("Service:"))
        self.cb_service = QComboBox()
        self.cb_service.currentTextChanged.connect(self.load_attendance)
        filter_layout.addWidget(self.cb_service)

        filter_layout.addWidget(QLabel("Year:"))
        self.cb_year = QComboBox()
        self.cb_year.currentTextChanged.connect(self.load_attendance)
        filter_layout.addWidget(self.cb_year)

        filter_layout.addWidget(QLabel("Month:"))
        self.cb_month = QComboBox()
        self.cb_month.currentTextChanged.connect(self.load_attendance)
        filter_layout.addWidget(self.cb_month)

        filter_layout.addWidget(QLabel("Date:"))
        self.cb_date = QComboBox()
        self.cb_date.currentTextChanged.connect(self.load_attendance)
        filter_layout.addWidget(self.cb_date)

        layout.addWidget(filter_group)

        # Summary Counters
        summary_layout = QHBoxLayout()
        self.lbl_total = QLabel("Total Records: 0")
        self.lbl_present = QLabel("Present: 0")
        self.lbl_absent = QLabel("Absent: 0")

        self.lbl_present.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.lbl_absent.setStyleSheet("color: #c0392b; font-weight: bold;")

        summary_layout.addWidget(self.lbl_total)
        summary_layout.addWidget(self.lbl_present)
        summary_layout.addWidget(self.lbl_absent)
        summary_layout.addStretch()

        layout.addLayout(summary_layout)

        # Attendance Table
        self.table = QTableWidget()
        self.headers = ["Member Name", "Service Type", "Date", "Status"]
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def populate_filters(self):
        self.cb_service.blockSignals(True)
        self.cb_year.blockSignals(True)
        self.cb_month.blockSignals(True)
        self.cb_date.blockSignals(True)

        self.cb_service.clear()
        self.cb_service.addItems(["All Services", "Sunday Morning Service", "Midweek Prayer", "Youth Service", "Special Event"])

        self.cb_year.clear()
        self.cb_year.addItems(["All Years", "2026", "2025"])

        self.cb_month.clear()
        self.cb_month.addItem("All Months", "All Months")
        months = [
            ("January", "01"), ("February", "02"), ("March", "03"), ("April", "04"),
            ("May", "05"), ("June", "06"), ("July", "07"), ("August", "08"),
            ("September", "09"), ("October", "10"), ("November", "11"), ("December", "12")
        ]
        for name, num in months:
            self.cb_month.addItem(name, num)

        self.refresh_date_dropdown()

        self.cb_service.blockSignals(False)
        self.cb_year.blockSignals(False)
        self.cb_month.blockSignals(False)
        self.cb_date.blockSignals(False)

    def refresh_date_dropdown(self):
        if not self.db:
            return

        all_records = self.db.get_attendance()
        unique_dates = sorted(list({r[2] for r in all_records}), reverse=True)

        self.cb_date.blockSignals(True)
        self.cb_date.clear()
        self.cb_date.addItem("All Dates")
        for d in unique_dates:
            self.cb_date.addItem(d)
        self.cb_date.blockSignals(False)

    def open_roll_call_dialog(self):
        dialog = RollCallDialog(self.db, self)
        if dialog.exec() == RollCallDialog.DialogCode.Accepted:
            self.refresh_date_dropdown()
            self.load_attendance()

    def load_attendance(self):
        if not self.db:
            return

        service = self.cb_service.currentText()
        year = self.cb_year.currentText()
        month_data = self.cb_month.currentData()
        date_val = self.cb_date.currentText()

        records = self.db.get_attendance(
            service_type=service,
            year=year,
            month_num=month_data,
            date_str=date_val
        )

        self.table.setRowCount(0)
        present_count = 0
        absent_count = 0

        for row_idx, record in enumerate(records):
            self.table.insertRow(row_idx)
            for col_idx, text in enumerate(record):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(text)))

            status = record[3]
            if status == "Present":
                present_count += 1
            elif status == "Absent":
                absent_count += 1

        self.lbl_total.setText(f"Total Records: {len(records)}")
        self.lbl_present.setText(f"Present: {present_count}")
        self.lbl_absent.setText(f"Absent: {absent_count}")

    def get_table_data(self):
        rows = []
        for row in range(self.table.rowCount()):
            row_data = [self.table.item(row, col).text() if self.table.item(row, col) else "" for col in range(self.table.columnCount())]
            rows.append(row_data)
        return rows

    def export_csv(self):
        rows = self.get_table_data()
        DataExporter.export_to_csv(self, self.headers, rows, "attendance_report.csv")

    def export_pdf(self):
        rows = self.get_table_data()
        DataExporter.export_to_pdf(self, "Attendance Analytics Report", self.headers, rows, "attendance_report.pdf")
