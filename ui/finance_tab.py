from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
    QComboBox, QLabel, QGroupBox
)
from utils.exporter import DataExporter
from ui.finance_dialog import AddTransactionDialog

class FinanceTab(QWidget):
    def __init__(self, db=None, user_role="Church Admin", parent=None):
        super().__init__(parent)
        self.db = db
        self.user_role = user_role
        self.init_ui()
        self.load_finances()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Action Buttons
        action_layout = QHBoxLayout()

        self.btn_add_trans = QPushButton("Record Transaction")
        self.btn_add_trans.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_add_trans.clicked.connect(self.open_add_dialog)

        is_admin = self.user_role in ["Main Admin", "Church Admin"]
        self.btn_add_trans.setEnabled(is_admin)

        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)

        self.export_pdf_btn = QPushButton("Export PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)

        action_layout.addWidget(self.btn_add_trans)
        action_layout.addWidget(self.export_csv_btn)
        action_layout.addWidget(self.export_pdf_btn)
        action_layout.addStretch()

        layout.addLayout(action_layout)

        # Summary Metrics Group
        metrics_group = QGroupBox("Financial Overview")
        metrics_layout = QHBoxLayout(metrics_group)

        self.lbl_income = QLabel("Total Income: GHS 0.00")
        self.lbl_income.setStyleSheet("font-size: 14px; font-weight: bold; color: #27ae60;")

        self.lbl_expense = QLabel("Total Expenses: GHS 0.00")
        self.lbl_expense.setStyleSheet("font-size: 14px; font-weight: bold; color: #c0392b;")

        self.lbl_balance = QLabel("Net Balance: GHS 0.00")
        self.lbl_balance.setStyleSheet("font-size: 14px; font-weight: bold; color: #2980b9;")

        metrics_layout.addWidget(self.lbl_income)
        metrics_layout.addWidget(self.lbl_expense)
        metrics_layout.addWidget(self.lbl_balance)

        layout.addWidget(metrics_group)

        # Filter Group
        filter_group = QGroupBox("Filter Transactions")
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("Type:"))
        self.cb_type_filter = QComboBox()
        self.cb_type_filter.addItems(["All Types", "Income", "Expense"])
        self.cb_type_filter.currentTextChanged.connect(self.load_finances)
        filter_layout.addWidget(self.cb_type_filter)

        filter_layout.addWidget(QLabel("Category:"))
        self.cb_cat_filter = QComboBox()
        self.cb_cat_filter.addItems(["All Categories", "Tithe", "Offering", "Donation", "Special Seed", "Utilities", "Maintenance", "Welfare", "Outreach", "Honorarium"])
        self.cb_cat_filter.currentTextChanged.connect(self.load_finances)
        filter_layout.addWidget(self.cb_cat_filter)

        filter_layout.addStretch()
        layout.addWidget(filter_group)

        # Transactions Table
        self.table = QTableWidget()
        self.headers = ["Type", "Category", "Amount (GHS)", "Date", "Payer/Payee", "Notes"]
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def open_add_dialog(self):
        dialog = AddTransactionDialog(self.db, self)
        if dialog.exec() == AddTransactionDialog.DialogCode.Accepted:
            self.load_finances()

    def load_finances(self):
        if not self.db:
            return

        trans_type = self.cb_type_filter.currentText()
        category = self.cb_cat_filter.currentText()

        records = self.db.get_finances(trans_type=trans_type, category=category)

        self.table.setRowCount(0)
        total_inc = 0.0
        total_exp = 0.0

        for row_idx, record in enumerate(records):
            # record: (trans_type, category, amount, date_str, member_name, notes)
            self.table.insertRow(row_idx)
            
            t_type, cat, amount, date_str, member, notes = record
            
            if t_type == "Income":
                total_inc += float(amount)
            else:
                total_exp += float(amount)

            formatted_record = [
                t_type, cat, f"{amount:.2f}", date_str, member or "-", notes or "-"
            ]

            for col_idx, text in enumerate(formatted_record):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(text)))

        net_balance = total_inc - total_exp
        self.lbl_income.setText(f"Total Income: GHS {total_inc:,.2f}")
        self.lbl_expense.setText(f"Total Expenses: GHS {total_exp:,.2f}")
        self.lbl_balance.setText(f"Net Balance: GHS {net_balance:,.2f}")

    def get_table_data(self):
        rows = []
        for row in range(self.table.rowCount()):
            row_data = [self.table.item(row, col).text() if self.table.item(row, col) else "" for col in range(self.table.columnCount())]
            rows.append(row_data)
        return rows

    def export_csv(self):
        rows = self.get_table_data()
        DataExporter.export_to_csv(self, self.headers, rows, "financial_report.csv")

    def export_pdf(self):
        rows = self.get_table_data()
        DataExporter.export_to_pdf(self, "Church Financial Statement", self.headers, rows, "financial_report.pdf")
