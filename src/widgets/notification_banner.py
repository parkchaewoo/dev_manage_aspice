"""알림 배너 위젯 - 마감일 경고"""
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class NotificationBanner(QFrame):
    """알림 배너 - 기한 초과 및 다가오는 마감일 표시"""

    dismissed = pyqtSignal()
    clicked = pyqtSignal()

    # Banner types
    TYPE_OVERDUE = "overdue"
    TYPE_UPCOMING = "upcoming"

    def __init__(self, banner_type=TYPE_OVERDUE, parent=None):
        super().__init__(parent)
        self.banner_type = banner_type
        self.expanded = False
        self.items = []
        self._setup_ui()

    def _setup_ui(self):
        if self.banner_type == self.TYPE_OVERDUE:
            bg_color = "#FF3B30"
            border_color = "#CC2F26"
            icon_text = "!!"
        else:
            bg_color = "#FF9500"
            border_color = "#CC7700"
            icon_text = "!"

        self.setStyleSheet(f"""
            NotificationBanner {{
                background-color: {bg_color};
                border-radius: 10px;
                border: 1px solid {border_color};
            }}
            QLabel {{
                color: white;
                background-color: transparent;
            }}
            QPushButton {{
                color: white;
                background-color: transparent;
                border: none;
                font-size: 16px;
                font-weight: bold;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 10, 14, 10)
        main_layout.setSpacing(4)

        # Top row: icon + message + dismiss button
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self.icon_label = QLabel(icon_text)
        icon_font = QFont("sans-serif", 14, QFont.Bold)
        self.icon_label.setFont(icon_font)
        self.icon_label.setFixedWidth(28)
        top_row.addWidget(self.icon_label)

        self.message_label = QLabel("No notifications")
        self.message_label.setFont(QFont("sans-serif", 12, QFont.Bold))
        self.message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.message_label.setCursor(Qt.PointingHandCursor)
        self.message_label.mousePressEvent = self._on_label_click
        top_row.addWidget(self.message_label)

        self.dismiss_btn = QPushButton("X")
        self.dismiss_btn.setFixedSize(28, 28)
        self.dismiss_btn.setCursor(Qt.PointingHandCursor)
        self.dismiss_btn.clicked.connect(self._on_dismiss)
        top_row.addWidget(self.dismiss_btn)

        main_layout.addLayout(top_row)

        # Detail area (initially hidden)
        self.detail_label = QLabel("")
        self.detail_label.setFont(QFont("sans-serif", 10))
        self.detail_label.setWordWrap(True)
        self.detail_label.setVisible(False)
        main_layout.addWidget(self.detail_label)

    def set_notifications(self, items):
        """알림 항목 설정: list of dict with project_name, name, due_date, swe_level"""
        self.items = items
        count = len(items)

        if count == 0:
            self.hide()
            return

        if self.banner_type == self.TYPE_OVERDUE:
            self.message_label.setText(
                f"{count} overdue milestone{'s' if count != 1 else ''} - click to expand"
            )
        else:
            self.message_label.setText(
                f"{count} upcoming deadline{'s' if count != 1 else ''} within 7 days - click to expand"
            )

        # Build detail text
        detail_lines = []
        for item in items[:10]:  # Show max 10
            project = item["project_name"] if "project_name" in item.keys() else "?"
            name = item["name"]
            due = item["due_date"] or "N/A"
            swe = item["swe_level"] if item["swe_level"] else ""
            line = f"  - [{project}] {name} (due: {due}){' / ' + swe if swe else ''}"
            detail_lines.append(line)
        if count > 10:
            detail_lines.append(f"  ... and {count - 10} more")

        self.detail_label.setText("\n".join(detail_lines))
        self.show()

    def _on_label_click(self, event):
        self.expanded = not self.expanded
        self.detail_label.setVisible(self.expanded)
        self.clicked.emit()

    def _on_dismiss(self):
        self.hide()
        self.dismissed.emit()
