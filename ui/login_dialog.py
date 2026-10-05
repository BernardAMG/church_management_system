from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)
from services.auth_service import AuthService

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Church Management System - Login")
        self.resize(350, 220)
        self.auth_service = AuthService()
        self.user_info = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        btn_layout = QHBoxLayout()
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        btn_layout.addWidget(login_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return

        user = self.auth_service.authenticate(username, password)
        if user:
            self.user_info = user
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Invalid username or password.")

    def get_user_info(self):
        return self.user_info
