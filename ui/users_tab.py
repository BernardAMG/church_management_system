from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QGroupBox, QFormLayout, QMenu, QAbstractItemView
)
from PyQt6.QtCore import Qt

class UserManagementTab(QWidget):
    def __init__(self, db=None, current_user=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_user = current_user or {}
        self.selected_user_id = None
        self.init_ui()
        self.load_users()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Form Group for Adding/Editing Users
        self.form_group = QGroupBox("Create New System User")
        form_layout = QFormLayout(self.form_group)

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Enter username")

        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("Enter password (leave blank to keep current password when editing)")

        self.cb_role = QComboBox()
        self.cb_role.addItems(["Church Admin", "Finance Officer", "Data Entry", "Main Admin"])

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_save_user = QPushButton("Create User Account")
        self.btn_save_user.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 6px;")
        self.btn_save_user.clicked.connect(self.save_user)

        self.btn_clear_form = QPushButton("Clear Selection / New User")
        self.btn_clear_form.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold; padding: 6px;")
        self.btn_clear_form.clicked.connect(self.reset_form)

        btn_layout.addWidget(self.btn_save_user)
        btn_layout.addWidget(self.btn_clear_form)

        form_layout.addRow("Username:", self.txt_username)
        form_layout.addRow("Password:", self.txt_password)
        form_layout.addRow("Role Assignment:", self.cb_role)
        form_layout.addRow(btn_layout)

        layout.addWidget(self.form_group)

        # Users Table Group
        table_group = QGroupBox("Existing User Accounts (Double-click a row for options)")
        table_layout = QVBoxLayout(table_group)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Assigned Role"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable in-cell typing
        
        # Connect double click to options menu
        self.table.itemDoubleClicked.connect(self.show_row_options_menu)
        table_layout.addWidget(self.table)

        # Bottom Actions
        btn_action_layout = QHBoxLayout()
        
        self.btn_edit_user = QPushButton("Edit Selected User")
        self.btn_edit_user.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold;")
        self.btn_edit_user.clicked.connect(self.load_selected_into_form)

        self.btn_delete_user = QPushButton("Delete Selected User")
        self.btn_delete_user.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold;")
        self.btn_delete_user.clicked.connect(self.delete_selected_user)

        btn_action_layout.addWidget(self.btn_edit_user)
        btn_action_layout.addWidget(self.btn_delete_user)
        btn_action_layout.addStretch()

        table_layout.addLayout(btn_action_layout)
        layout.addWidget(table_group)

    def load_users(self):
        if not self.db:
            return

        users = self.db.get_all_users()
        self.table.setRowCount(0)

        for row_idx, (u_id, username, role) in enumerate(users):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(u_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(username))
            self.table.setItem(row_idx, 2, QTableWidgetItem(role))

    def show_row_options_menu(self, item):
        row = item.row()
        username_item = self.table.item(row, 1)
        
        # Check if clicking on a valid populated row
        if not username_item or not username_item.text().strip():
            return

        username = username_item.text()

        # Pop-up context menu on double click
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { font-size: 14px; padding: 5px; } QMenu::item:selected { background-color: #2980b9; color: white; }")
        
        edit_action = menu.addAction(f"✏️ Edit User '{username}'")
        delete_action = menu.addAction(f"🗑️ Delete User '{username}'")
        replace_action = menu.addAction(f"🔄 Replace User '{username}'")

        action = menu.exec(self.cursor().pos())

        if action == edit_action:
            self.load_selected_into_form()
        elif action == delete_action:
            self.delete_selected_user()
        elif action == replace_action:
            self.replace_user_prompt()

    def load_selected_into_form(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a valid user row first.")
            return

        row = selected_rows[0].row()
        id_item = self.table.item(row, 0)
        username_item = self.table.item(row, 1)

        if not username_item or not username_item.text().strip():
            QMessageBox.warning(self, "Invalid Row", "Selected row does not contain a valid user.")
            return

        self.selected_user_id = int(id_item.text())
        username = username_item.text()
        role = self.table.item(row, 2).text()

        self.txt_username.setText(username)
        self.txt_password.clear()
        
        index = self.cb_role.findText(role)
        if index >= 0:
            self.cb_role.setCurrentIndex(index)

        self.form_group.setTitle(f"Editing User Account (ID: {self.selected_user_id} - {username})")
        self.btn_save_user.setText("Update User Account")
        self.btn_save_user.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; padding: 6px;")

    def replace_user_prompt(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        username = self.table.item(row, 1).text()

        reply = QMessageBox.question(
            self,
            "Confirm Replacement",
            f"Replacing '{username}' will delete this account and let you set up a new user in its place.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_selected_user(silent=True)
            self.reset_form()
            QMessageBox.information(self, "Ready to Replace", "Old account removed. Enter details for the new replacement user above.")

    def reset_form(self):
        self.selected_user_id = None
        self.txt_username.clear()
        self.txt_password.clear()
        self.cb_role.setCurrentIndex(0)
        self.form_group.setTitle("Create New System User")
        self.btn_save_user.setText("Create User Account")
        self.btn_save_user.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 6px;")

    def save_user(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        role = self.cb_role.currentText()

        if not username:
            QMessageBox.warning(self, "Validation Error", "Username cannot be empty.")
            return

        try:
            if self.selected_user_id:
                self.db.update_user(self.selected_user_id, username, password, role)
                QMessageBox.information(self, "Success", f"User '{username}' updated successfully.")
            else:
                if not password:
                    QMessageBox.warning(self, "Validation Error", "Password is required for new users.")
                    return
                self.db.add_user(username, password, role)
                QMessageBox.information(self, "Success", f"User '{username}' created successfully as {role}.")

            self.reset_form()
            self.load_users()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save user: {e}")

    def delete_selected_user(self, silent=False):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            if not silent:
                QMessageBox.warning(self, "Selection Error", "Please select a user from the table to delete.")
            return

        row = selected_rows[0].row()
        id_item = self.table.item(row, 0)
        username_item = self.table.item(row, 1)

        if not username_item or not username_item.text().strip():
            return

        user_id = int(id_item.text())
        username = username_item.text()

        if username == self.current_user.get("username"):
            QMessageBox.warning(self, "Action Denied", "You cannot delete your own logged-in account.")
            return

        if not silent:
            reply = QMessageBox.question(
                self, 
                "Confirm Delete", 
                f"Are you sure you want to delete user account '{username}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.db.delete_user(user_id)
        if self.selected_user_id == user_id:
            self.reset_form()
        self.load_users()
        if not silent:
            QMessageBox.information(self, "Deleted", f"User '{username}' deleted successfully.")
