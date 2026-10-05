from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QDateEdit, QPushButton, QMessageBox, QDoubleSpinBox, QFormLayout
)
from PyQt6.QtCore import QDate

class AddTransactionDialog(QDialog):
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Record Transaction")
        self.setMinimumWidth(380)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        # Type Selection
        self.cb_type = QComboBox()
        self.cb_type.addItems(["Income", "Expense"])
        self.cb_type.currentTextChanged.connect(self.update_categories)
        layout.addRow("Type:", self.cb_type)

        # Category Selection
        self.cb_category = QComboBox()
        layout.addRow("Category:", self.cb_category)

        # Amount Input
        self.spin_amount = QDoubleSpinBox()
        self.spin_amount.setRange(0.01, 1000000.00)
        self.spin_amount.setDecimals(2)
        self.spin_amount.setPrefix("GHS ")
        layout.addRow("Amount:", self.spin_amount)

        # Date Picker
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        layout.addRow("Date:", self.date_picker)

        # Contributor / Payee Name (Optional)
        self.txt_member = QLineEdit()
        self.txt_member.setPlaceholderText("Member / Vendor name (optional)")
        layout.addRow("Payer / Payee:", self.txt_member)

        # Notes
        self.txt_notes = QLineEdit()
        self.txt_notes.setPlaceholderText("Reference or memo")
        layout.addRow("Notes:", self.txt_notes)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save Record")
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_transaction)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addRow(btn_layout)

        self.update_categories()

    def update_categories(self):
        self.cb_category.clear()
        if self.cb_type.currentText() == "Income":
            self.cb_category.addItems(["Tithe", "Offering", "Donation", "Special Seed", "Other Income"])
        else:
            self.cb_category.addItems(["Utilities", "Maintenance", "Welfare", "Outreach", "Honorarium", "Other Expense"])

    def save_transaction(self):
        trans_type = self.cb_type.currentText()
        category = self.cb_category.currentText()
        amount = self.spin_amount.value()
        date_str = self.date_picker.date().toString("yyyy-MM-dd")
        member_name = self.txt_member.text().strip()
        notes = self.txt_notes.text().strip()

        if amount <= 0:
            QMessageBox.warning(self, "Validation Error", "Amount must be greater than zero.")
            return

        try:
            if self.db:
                self.db.add_financial_record(trans_type, category, amount, date_str, member_name, notes)
            QMessageBox.information(self, "Success", "Transaction recorded successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save transaction: {e}")
