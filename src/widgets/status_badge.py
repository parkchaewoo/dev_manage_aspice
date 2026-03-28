"""상태 표시 배지 위젯"""
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

from src.utils.constants import STATUS_COLORS


class StatusBadge(QLabel):
    """컬러 배경의 상태 배지"""

    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.update_status(status)

    def update_status(self, status):
        color = STATUS_COLORS.get(status, "#8E8E93")
        self.setText(f"  {status}  ")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            f"background-color: {color}; color: white; "
            f"border-radius: 8px; padding: 3px 10px; "
            f"font-size: 11px; font-weight: 600;"
        )
