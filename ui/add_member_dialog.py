import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout, 
    QLineEdit, QComboBox, QDialogButtonBox
)
from utils.exporter import DataExporter

class AddMemberDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Member")
        self.setMinimumWidth(350)
        
        layout = QFormLayout(self)
        
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female"])
        
        layout.addRow("First Name:", self.first_name_input)
        layout.addRow("Last Name:", self.last_name_input)
        layout.addRow("Phone Number:", self.phone_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Gender:", self.gender_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return [
            self.first_name_input.text().strip(),
            self.last_name_input.text().strip(),
            self.phone_input.text().strip(),
            self.email_input.text().strip(),
            self.gender_input.currentText()
        ]
