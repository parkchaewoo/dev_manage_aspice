"""Phase 히스토리 위젯 - Phase 로그 타임라인 표시"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

from src.models.database import get_connection
from src.models.phase_log import PhaseLogModel
from src.models.phase import PhaseModel


# Action type -> color mapping
ACTION_COLORS = {
    "created": "#007AFF",    # blue
    "inherited": "#34C759",  # green
    "modified": "#FF9500",   # orange
    "deleted": "#FF3B30",    # red
}


class PhaseHistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase_id = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        self.title_label = QLabel("Phase History / 단계 이력")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)

        # Scroll area for log cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.addStretch()

        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)

    def load_phase(self, phase_id):
        """Load and display logs for a phase."""
        self.phase_id = phase_id

        # Clear existing cards
        while self.scroll_layout.count() > 1:
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        conn = get_connection()
        phase = PhaseModel.get_by_id(phase_id, conn)
        if phase:
            self.title_label.setText(
                f"Phase History: {phase['name']} / 단계 이력: {phase['name']}"
            )

        logs = PhaseLogModel.get_by_phase(phase_id, conn)
        conn.close()

        if not logs:
            no_data = QLabel("No history records / 이력 기록 없음")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("color: #8E8E93; padding: 20px;")
            self.scroll_layout.insertWidget(0, no_data)
            return

        for log in logs:
            card = self._create_log_card(log)
            self.scroll_layout.insertWidget(
                self.scroll_layout.count() - 1, card
            )

    def _create_log_card(self, log):
        """Create a card widget for a single log entry."""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)

        action = log["action"]
        color = ACTION_COLORS.get(action, "#8E8E93")
        card.setStyleSheet(
            f"QFrame {{ border-left: 4px solid {color}; "
            f"background: #F9F9FB; border-radius: 6px; padding: 8px; }}"
        )

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(4)
        card_layout.setContentsMargins(12, 8, 8, 8)

        # Header row: action + timestamp
        header = QHBoxLayout()
        action_label = QLabel(action.upper())
        action_font = QFont()
        action_font.setBold(True)
        action_font.setPointSize(10)
        action_label.setFont(action_font)
        action_label.setStyleSheet(f"color: {color};")
        header.addWidget(action_label)

        header.addStretch()

        time_label = QLabel(str(log["created_at"]))
        time_label.setStyleSheet("color: #8E8E93; font-size: 10px;")
        header.addWidget(time_label)
        card_layout.addLayout(header)

        # Description
        if log["description"]:
            desc_label = QLabel(log["description"])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #3A3A3C;")
            card_layout.addWidget(desc_label)

        # Entity info
        info_parts = []
        if log["entity_type"]:
            info_parts.append(f"Type: {log['entity_type']}")
        if log["user_name"]:
            info_parts.append(f"User: {log['user_name']}")
        if info_parts:
            info_label = QLabel(" | ".join(info_parts))
            info_label.setStyleSheet("color: #AEAEB2; font-size: 10px;")
            card_layout.addWidget(info_label)

        return card
