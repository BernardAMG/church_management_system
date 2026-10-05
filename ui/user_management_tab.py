from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QComboBox, QMessageBox, QTabWidget,
    QGroupBox
)
from PyQt6.QtCore import Qt

class AddUserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setWindowTitle("Edit User" if user_data else "Create New User Account")
        self.resize(380, 260)

        layout = QFormLayout(self)

        self.username_input = QLineEdit()
        self.fullname_input = QLineEdit()
        
        self.role_input = QComboBox()
        self.role_input.addItems(["Admin", "Secretary", "Treasurer", "Viewer"])

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        if self.user_data:
            self.username_input.setText(self.user_data['username'])
            self.username_input.setEnabled(False)
            self.fullname_input.setText(self.user_data['full_name'])
            self.role_input.setCurrentText(self.user_data['role'])
            self.password_input.setPlaceholderText("(Leave blank to keep existing password)")
        else:
            self.password_input.setPlaceholderText("Enter secure password")

        layout.addRow("Username:", self.username_input)
        layout.addRow("Full Name:", self.fullname_input)
        layout.addRow("Assigned Role:", self.role_input)
        layout.addRow("Password:", self.password_input)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Account")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def get_data(self):
        return {
            "username": self.username_input.text().strip(),
            "full_name": self.fullname_input.text().strip(),
            "role": self.role_input.currentText(),
            "password": self.password_input.text().strip()
        }

class UserManagementTab(QWidget):
    def __init__(self, db, current_user):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.init_ui()
        self.load_users()
        self.load_audit_logs()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        self.sub_tabs = QTabWidget()

        # Tab 1: User Accounts List
        users_widget = QWidget()
        users_layout = QVBoxLayout(users_widget)

        toolbar = QHBoxLayout()
        title_lbl = QLabel("System User Accounts")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        toolbar.addWidget(title_lbl)

        toolbar.addStretch()

        add_user_btn = QPushButton("+ Add New User")
        add_user_btn.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 6px 12px;")
        add_user_btn.clicked.connect(self.open_add_user_dialog)
        toolbar.addWidget(add_user_btn)

        users_layout.addLayout(toolbar)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Full Name", "Role", "Status", "Actions"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        users_layout.addWidget(self.users_table)
        self.sub_tabs.addTab(users_widget, "User Accounts")

        # Tab 2: System Audit Trail
        audit_widget = QWidget()
        audit_layout = QVBoxLayout(audit_widget)

        audit_bar = QHBoxLayout()
        audit_title = QLabel("System Audit Trail & Security Logs")
        audit_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        audit_bar.addWidget(audit_title)

        audit_bar.addStretch()

        refresh_audit_btn = QPushButton("? Refresh Logs")
        refresh_audit_btn.setStyleSheet("background-color: #34495e; color: white; padding: 5px 12px; font-weight: bold;")
        refresh_audit_btn.clicked.connect(self.load_audit_logs)
        audit_bar.addWidget(refresh_audit_btn)

        audit_layout.addLayout(audit_bar)

        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(4)
        self.audit_table.setHorizontalHeaderLabels(["Timestamp", "User", "Action Executed", "Details"])
        self.audit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.audit_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.audit_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        audit_layout.addWidget(self.audit_table)
        self.sub_tabs.addTab(audit_widget, "Audit Logs")

        main_layout.addWidget(self.sub_tabs)

    def load_users(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, full_name, role, status FROM users ORDER BY id ASC")
            users = cursor.fetchall()

        self.users_table.setRowCount(0)
        for r_idx, u in enumerate(users):
            self.users_table.insertRow(r_idx)
            self.users_table.setItem(r_idx, 0, QTableWidgetItem(str(u[0])))
            self.users_table.setItem(r_idx, 1, QTableWidgetItem(str(u[1])))
            self.users_table.setItem(r_idx, 2, QTableWidgetItem(str(u[2])))
            self.users_table.setItem(r_idx, 3, QTableWidgetItem(str(u[3])))
            self.users_table.setItem(r_idx, 4, QTableWidgetItem(str(u[4])))

            # Action Buttons Panel
            actions_widget = QWidget()
            btn_layout = QHBoxLayout(actions_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)

            toggle_btn = QPushButton("Deactivate" if u[4] == 'Active' else "Activate")
            toggle_btn.setStyleSheet("background-color: #e74c3c; color: white; font-size: 11px;" if u[4] == 'Active' else "background-color: #27ae60; color: white; font-size: 11px;")
            toggle_btn.clicked.connect(lambda _, user_id=u[0], current_status=u[4]: self.toggle_user_status(user_id, current_status))

            reset_btn = QPushButton("Reset Password")
            reset_btn.setStyleSheet("background-color: #e67e22; color: white; font-size: 11px;")
            reset_btn.clicked.connect(lambda _, user_id=u[0], uname=u[1]: self.reset_user_password(user_id, uname))

            btn_layout.addWidget(toggle_btn)
            btn_layout.addWidget(reset_btn)

            self.users_table.setCellWidget(r_idx, 5, actions_widget)

    def load_audit_logs(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.timestamp, COALESCE(u.username, 'System'), a.action, a.details
                FROM audit_logs a
                LEFT JOIN users u ON a.user_id = u.id
                ORDER BY a.id DESC LIMIT 100
            ''')
            logs = cursor.fetchall()

        self.audit_table.setRowCount(0)
        for r_idx, log in enumerate(logs):
            self.audit_table.insertRow(r_idx)
            for c_idx, val in enumerate(log):
                self.audit_table.setItem(r_idx, c_idx, QTableWidgetItem(str(val) if val is not None else ""))

    def open_add_user_dialog(self):
        dialog = AddUserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["username"] or not data["full_name"] or not data["password"]:
                QMessageBox.warning(self, "Validation Error", "All fields are required.")
                return

            p_hash, p_salt = self.db.hash_password(data["password"])

            try:
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO users (username, password_hash, salt, full_name, role)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (data["username"], p_hash, p_salt, data["full_name"], data["role"]))
                    conn.commit()

                self.db.log_audit(
                    self.current_user.get('id'),
                    "CREATED_USER",
                    f"Created user account '{data['username']}' with role '{data['role']}'"
                )

                QMessageBox.information(self, "Success", f"User '{data['username']}' created successfully.")
                self.load_users()
                self.load_audit_logs()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to create user (Username may already exist): {e}")

    def toggle_user_status(self, user_id, current_status):
        new_status = "Suspended" if current_status == "Active" else "Active"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))
            conn.commit()

        self.db.log_audit(
            self.current_user.get('id'),
            "UPDATED_USER_STATUS",
            f"Changed user ID {user_id} status to '{new_status}'"
        )

        self.load_users()
        self.load_audit_logs()

    def reset_user_password(self, user_id, username):
        default_pwd = "ChangeMe123!"
        p_hash, p_salt = self.db.hash_password(default_pwd)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?", (p_hash, p_salt, user_id))
            conn.commit()

        self.db.log_audit(
            self.current_user.get('id'),
            "RESET_PASSWORD",
            f"Reset password for user '{username}' (ID: {user_id})"
        )

        QMessageBox.information(self, "Password Reset", f"Password for '{username}' has been reset to: {default_pwd}")
        self.load_audit_logs()
