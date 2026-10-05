import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QTabWidget, QDialog, 
    QLineEdit, QFormLayout, QMessageBox
)
from ui.dashboard_tab import ExecutiveDashboardTab
from ui.members_tab import MembersTab
from ui.attendance_tab import AttendanceTab
from ui.finance_tab import FinanceTab
from ui.users_tab import UserManagementTab
from utils.updater import SecureUpdater
from database import DatabaseManager

class LoginDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.authenticated_user = None
        self.setWindowTitle("Church Management System - Secure Login")
        self.setMinimumWidth(340)
        
        layout = QFormLayout(self)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Default: admin")
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Default: admin123")

        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)

        self.login_btn = QPushButton("Login")
        self.login_btn.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 6px;")
        self.login_btn.clicked.connect(self.attempt_login)
        layout.addRow(self.login_btn)

    def attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both username and password.")
            return

        user_data = self.db.authenticate_user(username, password)
        if user_data:
            self.authenticated_user = user_data
            self.accept()
        else:
            QMessageBox.critical(self, "Authentication Failed", "Invalid username or password.")

class MainWindow(QMainWindow):
    def __init__(self, user_info, db=None):
        super().__init__()
        self.user_info = user_info
        self.db = db or DatabaseManager()
        self.setWindowTitle(f"Church Management System - Logged in as: {user_info['username']} ({user_info['role']})")
        self.resize(1080, 720)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header Bar
        header_layout = QHBoxLayout()
        header_label = QLabel(f"<b>Welcome, {self.user_info['username']}</b> | Role: <font color='#2980b9'>{self.user_info['role']}</font>")
        
        self.btn_update = QPushButton("Check Secure Updates")
        self.btn_update.clicked.connect(lambda: SecureUpdater.check_for_updates(self))

        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        self.btn_logout.clicked.connect(self.handle_logout)

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_update)
        header_layout.addWidget(self.btn_logout)
        main_layout.addLayout(header_layout)

        # Tab Navigation based on Role-Based Access Control (RBAC)
        self.tabs = QTabWidget()
        
        role = self.user_info['role']

        # Tabs Setup
        self.dashboard_tab = ExecutiveDashboardTab(db=self.db)
        self.members_tab = MembersTab(db=self.db, user_role=role)
        self.attendance_tab = AttendanceTab(db=self.db)
        self.finance_tab = FinanceTab(db=self.db, user_role=role)

        if role in ["Main Admin", "Church Admin", "Finance Officer"]:
            self.tabs.addTab(self.dashboard_tab, "Executive Dashboard")

        self.tabs.addTab(self.members_tab, "Members Directory")
        self.tabs.addTab(self.attendance_tab, "Attendance Analytics")

        if role in ["Main Admin", "Church Admin", "Finance Officer"]:
            self.tabs.addTab(self.finance_tab, "Financial Management")

        if role == "Main Admin":
            self.users_tab = UserManagementTab(db=self.db, current_user=self.user_info)
            self.tabs.addTab(self.users_tab, "User Management")

        # Connect quick action signal from dashboard if visible
        if hasattr(self, 'dashboard_tab'):
            self.dashboard_tab.navigate_to_signal.connect(self.tabs.setCurrentIndex)

        self.tabs.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tabs)

    def on_tab_changed(self, index):
        current_widget = self.tabs.widget(index)
        if isinstance(current_widget, ExecutiveDashboardTab):
            current_widget.refresh_dashboard()

    def handle_logout(self):
        self.close()
        launch_app()

def launch_app():
    db = DatabaseManager()
    login = LoginDialog(db)
    if login.exec() == QDialog.DialogCode.Accepted:
        user_info = login.authenticated_user
        window = MainWindow(user_info, db=db)
        window.show()
        app.active_window = window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launch_app()
    sys.exit(app.exec())
