"""문서 리뷰/승인 상태 위젯"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from src.models.document import DocumentModel
from src.utils.constants import DocumentStatus, STATUS_COLORS


class ReviewStatusWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stage_id = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 요약
        self.summary_frame = QFrame()
        self.summary_frame.setProperty("card", True)
        summary_layout = QHBoxLayout(self.summary_frame)

        self.draft_count = self._status_badge("Draft", "#8E8E93", "0")
        self.review_count = self._status_badge("In Review", "#FF9500", "0")
        self.approved_count = self._status_badge("Approved", "#34C759", "0")
        self.rejected_count = self._status_badge("Rejected", "#FF3B30", "0")

        for badge in [self.draft_count, self.review_count, self.approved_count, self.rejected_count]:
            summary_layout.addWidget(badge)

        layout.addWidget(self.summary_frame)

        # 문서 리뷰 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Document / 문서", "Current Status / 현재 상태",
            "Action / 다음 단계", ""
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def _status_badge(self, label, color, count):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ background-color: {color}20; border-radius: 10px; padding: 8px; }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)

        count_lbl = QLabel(count)
        count_lbl.setAlignment(Qt.AlignCenter)
        count_lbl.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        count_lbl.setObjectName(f"count_{label.replace(' ', '_')}")
        layout.addWidget(count_lbl)

        name_lbl = QLabel(label)
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setStyleSheet(f"font-size: 11px; color: {color};")
        layout.addWidget(name_lbl)

        return frame

    def load_stage(self, stage_id, conn=None):
        """단계의 리뷰 상태 로드"""
        self.stage_id = stage_id
        from src.models.database import get_connection
        should_close = conn is None
        if conn is None:
            conn = get_connection()

        docs = DocumentModel.get_by_stage(stage_id, conn)

        # 요약 업데이트
        counts = {s: 0 for s in DocumentStatus.ALL}
        for doc in docs:
            counts[doc["status"]] = counts.get(doc["status"], 0) + 1

        self._update_badge_count(self.draft_count, counts.get(DocumentStatus.DRAFT, 0))
        self._update_badge_count(self.review_count, counts.get(DocumentStatus.IN_REVIEW, 0))
        self._update_badge_count(self.approved_count, counts.get(DocumentStatus.APPROVED, 0))
        self._update_badge_count(self.rejected_count, counts.get(DocumentStatus.REJECTED, 0))

        # 테이블 업데이트
        self.table.setRowCount(len(docs))
        for i, doc in enumerate(docs):
            self.table.setItem(i, 0, QTableWidgetItem(doc["name"]))

            status_item = QTableWidgetItem(f"  {doc['status']}  ")
            color = STATUS_COLORS.get(doc["status"], "#8E8E93")
            status_item.setBackground(QColor(color))
            status_item.setForeground(QColor("white"))
            self.table.setItem(i, 1, status_item)

            # 가능한 다음 액션
            transitions = DocumentStatus.TRANSITIONS.get(doc["status"], [])
            if transitions:
                combo = QComboBox()
                combo.addItem("-- Select --")
                combo.addItems(transitions)
                combo.currentTextChanged.connect(
                    lambda new_status, did=doc["id"]: self._transition(did, new_status)
                )
                self.table.setCellWidget(i, 2, combo)
            else:
                self.table.setItem(i, 2, QTableWidgetItem("Complete"))

            self.table.setItem(i, 3, QTableWidgetItem(""))

        if should_close:
            conn.close()

    def _update_badge_count(self, badge_frame, count):
        for child in badge_frame.findChildren(QLabel):
            if child.objectName().startswith("count_"):
                child.setText(str(count))
                break

    def _transition(self, doc_id, new_status):
        if new_status == "-- Select --":
            return
        DocumentModel.update(doc_id, status=new_status)
        self.load_stage(self.stage_id)
