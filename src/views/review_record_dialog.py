"""리뷰 기록 생성/편집 다이얼로그"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QTextEdit, QPushButton, QFormLayout,
    QDialogButtonBox
)
from PyQt5.QtCore import Qt, QDate

from src.models.review_record import ReviewRecordModel


class ReviewRecordDialog(QDialog):
    """리뷰 기록을 생성하거나 편집하는 다이얼로그"""

    def __init__(self, document_id, record_id=None, parent=None):
        super().__init__(parent)
        self.document_id = document_id
        self.record_id = record_id
        self.setWindowTitle("Review Record / 리뷰 기록")
        self.setMinimumWidth(520)
        self.setMinimumHeight(560)
        self._setup_ui()
        if record_id:
            self._load_record(record_id)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        # Review Type / 리뷰 유형
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Formal", "Informal", "Walkthrough"])
        form.addRow("Review Type / 리뷰 유형:", self.type_combo)

        # Review Date / 리뷰 일자
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form.addRow("Review Date / 리뷰 일자:", self.date_edit)

        # Participants / 참석자
        self.participants_edit = QLineEdit()
        self.participants_edit.setPlaceholderText("Comma-separated / 쉼표로 구분")
        form.addRow("Participants / 참석자:", self.participants_edit)

        # Findings / 지적사항
        self.findings_edit = QTextEdit()
        self.findings_edit.setPlaceholderText("Review findings / 리뷰 지적사항...")
        self.findings_edit.setMaximumHeight(100)
        form.addRow("Findings / 지적사항:", self.findings_edit)

        # Action Items / 조치항목
        self.action_items_edit = QTextEdit()
        self.action_items_edit.setPlaceholderText("Action items / 조치항목...")
        self.action_items_edit.setMaximumHeight(100)
        form.addRow("Action Items / 조치항목:", self.action_items_edit)

        # Decisions / 결정사항
        self.decisions_edit = QTextEdit()
        self.decisions_edit.setPlaceholderText("Decisions / 결정사항...")
        self.decisions_edit.setMaximumHeight(80)
        form.addRow("Decisions / 결정사항:", self.decisions_edit)

        # Result / 결과
        self.result_combo = QComboBox()
        self.result_combo.addItems(["Approved", "Rejected", "Open"])
        self.result_combo.setCurrentText("Open")
        form.addRow("Result / 결과:", self.result_combo)

        # Notes / 비고
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Additional notes / 추가 메모...")
        form.addRow("Notes / 비고:", self.notes_edit)

        layout.addLayout(form)

        # Buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        btn_box.accepted.connect(self._save)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _load_record(self, record_id):
        """기존 리뷰 기록 로드"""
        record = ReviewRecordModel.get_by_id(record_id)
        if not record:
            return
        self.type_combo.setCurrentText(record["review_type"])
        if record["review_date"]:
            self.date_edit.setDate(QDate.fromString(record["review_date"], "yyyy-MM-dd"))
        self.participants_edit.setText(record["participants"] or "")
        self.findings_edit.setPlainText(record["findings"] or "")
        self.action_items_edit.setPlainText(record["action_items"] or "")
        self.decisions_edit.setPlainText(record["decisions"] or "")
        self.result_combo.setCurrentText(record["result"] or "Open")
        self.notes_edit.setText(record["notes"] or "")

    def _save(self):
        """리뷰 기록 저장"""
        data = {
            "review_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "review_type": self.type_combo.currentText(),
            "participants": self.participants_edit.text(),
            "findings": self.findings_edit.toPlainText(),
            "action_items": self.action_items_edit.toPlainText(),
            "decisions": self.decisions_edit.toPlainText(),
            "result": self.result_combo.currentText(),
            "notes": self.notes_edit.text(),
        }

        if self.record_id:
            ReviewRecordModel.update(self.record_id, **data)
        else:
            ReviewRecordModel.create(
                document_id=self.document_id,
                **data
            )
        self.accept()
