from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class DashboardTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Dashboard Overview</h2>"))

class MembersTab(QWidget):
    def __init__(self, db, current_role='Admin'):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Members Management</h2>"))

class FinancialsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Financials Management</h2>"))

class AttendanceTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Attendance Tracking</h2>"))

class ReportsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>System Reports</h2>"))
