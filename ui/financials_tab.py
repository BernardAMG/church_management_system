from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QComboBox, QDoubleSpinBox, QMessageBox,
    QFrame
)
from PyQt6.QtCore import Qt
from utils.exporter import DataExporter

class AddTransactionDialog(QDialog):
    def __init__(self, members_list, parent=None):
        super().__init__(parent)
        self.members_list = members_list
        self.setWindowTitle("Record Transaction")
        self.resize(400, 320)

        layout = QFormLayout(self)

        self.type_input = QComboBox()
        self.type_input.addItems(["Income", "Expense"])
        self.type_input.currentTextChanged.connect(self.update_categories)

        self.category_input = QComboBox()

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 1000000.00)
        self.amount_input.setDecimals(2)

        self.member_input = QComboBox()
        self.member_input.addItem("Anonymous / General", None)
        for m_id, name in self.members_list:
            self.member_input.addItem(f"{name} (ID: {m_id})", m_id)

        self.desc_input = QLineEdit()

        layout.addRow("Transaction Type:", self.type_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Amount (GH?):", self.amount_input)
        layout.addRow("Member (Optional):", self.member_input)
        layout.addRow("Description / Note:", self.desc_input)

        self.update_categories()

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Transaction")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addRow(btn_layout)

    def update_categories(self):
        self.category_input.clear()
        if self.type_input.currentText() == "Income":
            self.category_input.addItems(["Tithe", "Offertory", "Special Seed / Donation", "Building Fund", "Other Income"])
            self.member_input.setEnabled(True)
        else:
            self.category_input.addItems(["Utilities & Electricity", "Equipment & Audio", "Welfare & Charity", "Maintenance", "Honorarium", "Other Expense"])
            self.member_input.setCurrentIndex(0)
            self.member_input.setEnabled(False)

    def get_data(self):
        return {
            "trans_type": self.type_input.currentText(),
            "category": self.category_input.currentText(),
            "amount": self.amount_input.value(),
            "member_id": self.member_input.currentData(),
            "description": self.desc_input.text().strip()
        }

class FinancialsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Financial Summary Cards Bar
        cards_layout = QHBoxLayout()
        self.income_card = self.create_summary_card("Total Income", "GH? 0.00", "#27ae60")
        self.expense_card = self.create_summary_card("Total Expenses", "GH? 0.00", "#c0392b")
        self.balance_card = self.create_summary_card("Net Balance", "GH? 0.00", "#2980b9")

        cards_layout.addWidget(self.income_card['frame'])
        cards_layout.addWidget(self.expense_card['frame'])
        cards_layout.addWidget(self.balance_card['frame'])
        main_layout.addLayout(cards_layout)

        # Action & Filter Bar
        action_layout = QHBoxLayout()
        self.filter_type = QComboBox()
        self.filter_type.addItems(["All Types", "Income", "Expense"])
        self.filter_type.currentTextChanged.connect(self.load_data)
        action_layout.addWidget(QLabel("Filter:"))
        action_layout.addWidget(self.filter_type)

        action_layout.addStretch()

        csv_btn = QPushButton("Export CSV")
        csv_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 6px 12px; font-weight: bold;")
        csv_btn.clicked.connect(self.export_csv)
        action_layout.addWidget(csv_btn)

        pdf_btn = QPushButton("Export PDF Report")
        pdf_btn.setStyleSheet("background-color: #e67e22; color: white; padding: 6px 12px; font-weight: bold;")
        pdf_btn.clicked.connect(self.export_pdf)
        action_layout.addWidget(pdf_btn)

        add_btn = QPushButton("+ Record Transaction")
        add_btn.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 6px 12px;")
        add_btn.clicked.connect(self.open_add_dialog)
        action_layout.addWidget(add_btn)

        main_layout.addLayout(action_layout)

        # Transactions Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Type", "Category", "Amount (GH?)", "Member", "Description", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        main_layout.addWidget(self.table)

    def create_summary_card(self, title, default_val, color_hex):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: #ffffff; border-left: 5px solid {color_hex}; border-radius: 4px; padding: 10px;")
        layout = QVBoxLayout(frame)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #7f8c8d; font-size: 12px; font-weight: bold;")
        val_lbl = QLabel(default_val)
        val_lbl.setStyleSheet(f"color: {color_hex}; font-size: 20px; font-weight: bold;")
        layout.addWidget(title_lbl)
        layout.addWidget(val_lbl)
        return {'frame': frame, 'label': val_lbl}

    def get_table_data(self):
        headers = ["ID", "Type", "Category", "Amount (GH?)", "Member", "Description", "Date"]
        rows = []
        for r in range(self.table.rowCount()):
            row_data = [self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(self.table.columnCount())]
            rows.append(row_data)
        return headers, rows

    def export_csv(self):
        headers, rows = self.get_table_data()
        DataExporter.export_to_csv(self, headers, rows, "financial_records.csv")

    def export_pdf(self):
        headers, rows = self.get_table_data()
        DataExporter.export_to_pdf(self, "Financial Transactions Report", headers, rows, "financial_report.pdf")

    def load_data(self):
        filter_val = self.filter_type.currentText()
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT SUM(amount) FROM financials WHERE trans_type = 'Income'")
            tot_income = cursor.fetchone()[0] or 0.0

            cursor.execute("SELECT SUM(amount) FROM financials WHERE trans_type = 'Expense'")
            tot_expense = cursor.fetchone()[0] or 0.0

            net_balance = tot_income - tot_expense

            self.income_card['label'].setText(f"GH? {tot_income:,.2f}")
            self.expense_card['label'].setText(f"GH? {tot_expense:,.2f}")
            self.balance_card['label'].setText(f"GH? {net_balance:,.2f}")

            base_query = '''
                SELECT f.id, f.trans_type, f.category, f.amount, 
                       COALESCE(m.full_name, 'N/A') as member_name, 
                       f.description, f.trans_date
                FROM financials f
                LEFT JOIN members m ON f.member_id = m.id
            '''
            if filter_val == "Income":
                base_query += " WHERE f.trans_type = 'Income'"
            elif filter_val == "Expense":
                base_query += " WHERE f.trans_type = 'Expense'"

            base_query += " ORDER BY f.id DESC"
            cursor.execute(base_query)
            rows = cursor.fetchall()

        self.table.setRowCount(0)
        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, item in enumerate(row):
                if col_idx == 3:
                    formatted = f"GH? {item:,.2f}"
                else:
                    formatted = str(item) if item is not None else ""
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(formatted))

    def get_members_list(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, full_name FROM members ORDER BY full_name ASC")
            return cursor.fetchall()

    def open_add_dialog(self):
        members = self.get_members_list()
        dialog = AddTransactionDialog(members, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data["amount"] <= 0:
                QMessageBox.warning(self, "Error", "Amount must be greater than zero.")
                return

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO financials (trans_type, category, amount, member_id, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (data["trans_type"], data["category"], data["amount"], data["member_id"], data["description"]))
                conn.commit()

            QMessageBox.information(self, "Success", "Transaction recorded successfully!")
            self.load_data()
