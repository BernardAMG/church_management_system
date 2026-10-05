from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QGridLayout
)
from PyQt6.QtCore import pyqtSignal

class ExecutiveDashboardTab(QWidget):
    # Signals to trigger tab navigation in MainWindow
    navigate_to_signal = pyqtSignal(int)

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
        self.refresh_dashboard()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header Bar & Refresh
        header_layout = QHBoxLayout()
        title_label = QLabel("Executive Dashboard Overview")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        self.btn_refresh = QPushButton("Refresh Data")
        self.btn_refresh.clicked.connect(self.refresh_dashboard)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_refresh)
        layout.addLayout(header_layout)

        # Metrics Grid (2x3)
        grid_layout = QGridLayout()

        # Card 1: Active Members
        self.card_active = self.create_metric_card("Active Membership", "0 / 0 Total", "#2980b9")
        grid_layout.addWidget(self.card_active, 0, 0)

        # Card 2: Attendance Rate
        self.card_attendance = self.create_metric_card("Avg Attendance Rate", "0.0%", "#27ae60")
        grid_layout.addWidget(self.card_attendance, 0, 1)

        # Card 3: Total Income
        self.card_income = self.create_metric_card("Total Income", "GHS 0.00", "#16a085")
        grid_layout.addWidget(self.card_income, 0, 2)

        # Card 4: Total Expenses
        self.card_expense = self.create_metric_card("Total Expenses", "GHS 0.00", "#c0392b")
        grid_layout.addWidget(self.card_expense, 1, 0)

        # Card 5: Net Financial Balance
        self.card_balance = self.create_metric_card("Net Financial Balance", "GHS 0.00", "#8e44ad")
        grid_layout.addWidget(self.card_balance, 1, 1)

        layout.addLayout(grid_layout)

        # Quick Actions Shortcuts Group
        actions_group = QGroupBox("Quick Action Shortcuts")
        actions_layout = QHBoxLayout(actions_group)

        btn_add_member = QPushButton("+ Add New Member")
        btn_add_member.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 10px;")
        btn_add_member.clicked.connect(lambda: self.navigate_to_signal.emit(1))  # Switch to Members Tab

        btn_take_attendance = QPushButton("Take Service Roll Call")
        btn_take_attendance.setStyleSheet("background-color: #d35400; color: white; font-weight: bold; padding: 10px;")
        btn_take_attendance.clicked.connect(lambda: self.navigate_to_signal.emit(2))  # Switch to Attendance Tab

        btn_record_trans = QPushButton("$ Record Transaction")
        btn_record_trans.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        btn_record_trans.clicked.connect(lambda: self.navigate_to_signal.emit(3))  # Switch to Finances Tab

        actions_layout.addWidget(btn_add_member)
        actions_layout.addWidget(btn_take_attendance)
        actions_layout.addWidget(btn_record_trans)

        layout.addWidget(actions_group)
        layout.addStretch()

    def create_metric_card(self, title, default_val, header_color):
        card = QGroupBox()
        card_layout = QVBoxLayout(card)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {header_color};")

        lbl_val = QLabel(default_val)
        lbl_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-top: 5px;")
        card.lbl_val = lbl_val  # Save reference for updates

        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_val)
        return card

    def refresh_dashboard(self):
        if not self.db:
            return

        summary = self.db.get_dashboard_summary()

        self.card_active.lbl_val.setText(f"{summary['active_members']} / {summary['total_members']} Active")
        self.card_attendance.lbl_val.setText(f"{summary['attendance_rate']:.1f}%")
        self.card_income.lbl_val.setText(f"GHS {summary['total_income']:,.2f}")
        self.card_expense.lbl_val.setText(f"GHS {summary['total_expense']:,.2f}")
        self.card_balance.lbl_val.setText(f"GHS {summary['net_balance']:,.2f}")
