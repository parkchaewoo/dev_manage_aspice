"""SWE 단계 상세 뷰"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTabWidget, QPushButton, QComboBox, QTextEdit, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from src.models.database import get_connection
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.project import ProjectModel
from src.models.oem import OemModel
from src.utils.constants import SWE_STAGES, STATUS_COLORS, StageStatus, DocumentStatus
from src.views.checklist_widget import ChecklistWidget
from src.views.review_status_widget import ReviewStatusWidget
from src.views.document_editor import DocumentEditorWidget
from src.views.test_result_widget import TestResultWidget
from src.views.attachment_widget import AttachmentWidget
from src.views.review_record_dialog import ReviewRecordDialog
from src.models.document import DocumentModel
from src.models.review_record import ReviewRecordModel


class StageDetailWidget(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stage_id = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 상단 네비게이션
        nav = QHBoxLayout()
        self.btn_back = QPushButton("< Back / 뒤로")
        self.btn_back.setProperty("secondary", True)
        self.btn_back.setMaximumWidth(150)
        self.btn_back.clicked.connect(self.back_requested.emit)
        nav.addWidget(self.btn_back)
        nav.addStretch()

        self.status_combo = QComboBox()
        self.status_combo.addItems(StageStatus.ALL)
        self.status_combo.currentTextChanged.connect(self._on_status_changed)
        nav.addWidget(QLabel("Status:"))
        nav.addWidget(self.status_combo)
        layout.addLayout(nav)

        # 제목
        self.title_label = QLabel()
        self.title_label.setProperty("heading", True)
        layout.addWidget(self.title_label)

        self.subtitle_label = QLabel()
        self.subtitle_label.setProperty("subheading", True)
        layout.addWidget(self.subtitle_label)

        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(16)

        # 탭 위젯
        self.tabs = QTabWidget()

        # 문서 탭
        self.doc_widget = DocumentEditorWidget()
        self.tabs.addTab(self.doc_widget, "Documents / 문서")

        # 체크리스트 탭
        self.checklist_widget = ChecklistWidget()
        self.tabs.addTab(self.checklist_widget, "Checklist / 체크리스트")

        # 리뷰 상태 탭
        self.review_widget = ReviewStatusWidget()
        self.tabs.addTab(self.review_widget, "Review / 리뷰")

        # 리뷰 기록 탭
        review_records_widget = QWidget()
        rr_layout = QVBoxLayout(review_records_widget)
        rr_top = QHBoxLayout()
        self.rr_doc_combo = QComboBox()
        self.rr_doc_combo.currentIndexChanged.connect(self._load_review_records)
        rr_top.addWidget(QLabel("Document / 문서:"))
        rr_top.addWidget(self.rr_doc_combo, 1)
        self.btn_add_review_record = QPushButton("Add Review Record / 리뷰 기록 추가")
        self.btn_add_review_record.clicked.connect(self._on_add_review_record)
        rr_top.addWidget(self.btn_add_review_record)
        rr_layout.addLayout(rr_top)

        self.rr_table = QTableWidget()
        self.rr_table.setColumnCount(6)
        self.rr_table.setHorizontalHeaderLabels([
            "Date / 일자", "Type / 유형", "Participants / 참석자",
            "Result / 결과", "Findings / 지적사항", "Action Items / 조치항목"
        ])
        from PyQt5.QtWidgets import QHeaderView as _HV
        self.rr_table.horizontalHeader().setSectionResizeMode(_HV.Stretch)
        self.rr_table.verticalHeader().setVisible(False)
        rr_layout.addWidget(self.rr_table)
        self.tabs.addTab(review_records_widget, "Review Records / 리뷰 기록")

        # 시험 결과 탭 (SWE.4/5/6)
        self.test_result_widget = TestResultWidget()
        self.tabs.addTab(self.test_result_widget, "Test Results / 시험 결과")

        # 첨부파일 탭
        self.attachment_widget = AttachmentWidget()
        self.tabs.addTab(self.attachment_widget, "Attachments / 첨부파일")

        # 노트 탭
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter notes here... / 메모를 입력하세요...")
        notes_layout.addWidget(self.notes_edit)
        save_btn = QPushButton("Save Notes / 메모 저장")
        save_btn.clicked.connect(self._save_notes)
        notes_layout.addWidget(save_btn)
        self.tabs.addTab(notes_widget, "Notes / 메모")

        scroll_layout.addWidget(self.tabs)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)

    def load_stage(self, stage_id):
        """단계 데이터 로드"""
        self.stage_id = stage_id
        conn = get_connection()

        stage = StageModel.get_by_id(stage_id, conn)
        if not stage:
            conn.close()
            return

        swe = stage["swe_level"]
        swe_info = SWE_STAGES.get(swe, {})
        project = ProjectModel.get_by_id(stage["project_id"], conn)
        oem = OemModel.get_by_id(project["oem_id"], conn) if project else None

        # 제목 업데이트
        self.title_label.setText(f"{swe}: {swe_info.get('name_ko', swe)}")
        self.subtitle_label.setText(
            f"{swe_info.get('name_en', '')}  |  "
            f"{oem['name'] if oem else ''} > {project['name'] if project else ''}"
        )

        # 상태 콤보 업데이트
        self.status_combo.blockSignals(True)
        idx = self.status_combo.findText(stage["status"])
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)
        self.status_combo.blockSignals(False)

        # 노트
        self.notes_edit.setText(stage["notes"] or "")

        # 하위 위젯 로드
        self.doc_widget.load_stage(stage_id, conn)
        self.checklist_widget.load_stage(stage_id, conn)
        self.review_widget.load_stage(stage_id, conn)

        # 리뷰 기록 문서 콤보 로드
        self.rr_doc_combo.blockSignals(True)
        self.rr_doc_combo.clear()
        self._rr_docs = DocumentModel.get_by_stage(stage_id, conn)
        for doc in self._rr_docs:
            self.rr_doc_combo.addItem(doc["name"], doc["id"])
        self.rr_doc_combo.blockSignals(False)
        if self._rr_docs:
            self._load_review_records()

        # 시험 결과 로드 (SWE.4/5/6만 탭 활성화)
        test_tab_idx = self.tabs.indexOf(self.test_result_widget)
        if swe in ("SWE.4", "SWE.5", "SWE.6"):
            self.tabs.setTabEnabled(test_tab_idx, True)
            self.test_result_widget.load_stage(stage_id, conn)
        else:
            self.tabs.setTabEnabled(test_tab_idx, False)

        # 첨부파일 로드
        self.attachment_widget.load_stage(stage_id, conn)

        conn.close()

    def _on_status_changed(self, new_status):
        if self.stage_id:
            StageModel.update(self.stage_id, status=new_status)

    def _save_notes(self):
        if self.stage_id:
            StageModel.update(self.stage_id, notes=self.notes_edit.toPlainText())

    def _load_review_records(self):
        """선택된 문서의 리뷰 기록 로드"""
        doc_id = self.rr_doc_combo.currentData()
        if not doc_id:
            self.rr_table.setRowCount(0)
            return
        records = ReviewRecordModel.get_by_document(doc_id)
        self.rr_table.setRowCount(len(records))
        for i, rec in enumerate(records):
            self.rr_table.setItem(i, 0, QTableWidgetItem(rec["review_date"] or ""))
            self.rr_table.setItem(i, 1, QTableWidgetItem(rec["review_type"] or ""))
            self.rr_table.setItem(i, 2, QTableWidgetItem(rec["participants"] or ""))
            self.rr_table.setItem(i, 3, QTableWidgetItem(rec["result"] or ""))
            self.rr_table.setItem(i, 4, QTableWidgetItem(
                (rec["findings"] or "")[:80]
            ))
            self.rr_table.setItem(i, 5, QTableWidgetItem(
                (rec["action_items"] or "")[:80]
            ))

    def _on_add_review_record(self):
        """리뷰 기록 추가"""
        doc_id = self.rr_doc_combo.currentData()
        if not doc_id:
            return
        from PyQt5.QtWidgets import QDialog
        dlg = ReviewRecordDialog(doc_id, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            self._load_review_records()
