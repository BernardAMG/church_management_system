import re
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, 
    QDialogButtonBox, QMessageBox
)

class AddMemberDialog(QDialog):
    def __init__(self, parent=None, member_data=None):
        super().__init__(parent)
        self.member_data = member_data
        self.setWindowTitle("Edit Member" if member_data else "Add New Member")
        self.setMinimumWidth(380)

        layout = QFormLayout(self)

        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.gender = QComboBox()
        self.gender.addItems(["Male", "Female"])
        self.status = QComboBox()
        self.status.addItems(["Active", "Inactive", "Visitor", "Suspended"])

        layout.addRow("First Name *:", self.first_name)
        layout.addRow("Last Name *:", self.last_name)
        layout.addRow("Phone (10 Digits) *:", self.phone)
        layout.addRow("Email Address:", self.email)
        layout.addRow("Gender:", self.gender)
        layout.addRow("Membership Status:", self.status)

        # Pre-fill data if editing
        if self.member_data:
            full_name = self.member_data[0].split(" ", 1)
            self.first_name.setText(full_name[0])
            if len(full_name) > 1:
                self.last_name.setText(full_name[1])
            self.phone.setText(self.member_data[1])
            self.email.setText(self.member_data[2])
            self.gender.setCurrentText(self.member_data[3])
            self.status.setCurrentText(self.member_data[4])

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def validate_and_accept(self):
        first = self.first_name.text().strip()
        last = self.last_name.text().strip()
        phone = self.phone.text().strip()

        if not first or not last:
            QMessageBox.warning(self, "Validation Error", "First and Last Name are required.")
            return

        # 10-Digit Phone Validation Rule
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        if not clean_phone.isdigit() or len(clean_phone) != 10:
            QMessageBox.warning(
                self, 
                "Invalid Phone Number", 
                "Phone number must contain exactly 10 numeric digits (e.g., 0241234567)."
            )
            return

        self.accept()

    def get_data(self):
        clean_phone = re.sub(r'[\s\-\(\)]', '', self.phone.text().strip())
        return [
            f"{self.first_name.text().strip()} {self.last_name.text().strip()}",
            clean_phone,
            self.email.text().strip(),
            self.gender.currentText(),
            self.status.currentText()
        ]
