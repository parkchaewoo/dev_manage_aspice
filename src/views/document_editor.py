"""문서 편집기 / 목록 위젯"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QPushButton, QComboBox,
    QHeaderView, QTextBrowser, QTextEdit, QDialog, QLineEdit, QFormLayout,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

import os
from datetime import date

from src.models.document import DocumentModel
from src.utils.constants import DocumentStatus, STATUS_COLORS


class DocumentEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stage_id = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 헤더
        header = QHBoxLayout()
        header.addWidget(QLabel("Documents / 문서 목록"))
        self.btn_add = QPushButton("+ Add Document")
        self.btn_add.setProperty("secondary", True)
        self.btn_add.setMaximumWidth(160)
        self.btn_add.clicked.connect(self._add_document)
        header.addStretch()
        header.addWidget(self.btn_add)
        layout.addLayout(header)

        self._selected_doc_id = None

        # 문서 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Document Name / 문서명", "Status / 상태", "Reviewer / 검토자", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self.table)

        # 문서 편집기 (Rich Editor)
        self.content_edit = QTextEdit()
        self.content_edit.setMinimumHeight(200)
        self.content_edit.setPlaceholderText(
            "Select a document and edit content here / 문서를 선택하고 여기서 내용을 편집하세요"
        )
        layout.addWidget(self.content_edit)

        # Save Content 버튼
        save_content_layout = QHBoxLayout()
        save_content_layout.addStretch()
        self.btn_save_content = QPushButton("Save Content / 내용 저장")
        self.btn_save_content.setMaximumWidth(200)
        self.btn_save_content.clicked.connect(self._save_content)
        save_content_layout.addWidget(self.btn_save_content)
        layout.addLayout(save_content_layout)

    def load_stage(self, stage_id, conn=None):
        """단계의 문서 목록 로드"""
        self.stage_id = stage_id
        from src.models.database import get_connection
        should_close = conn is None
        if conn is None:
            conn = get_connection()

        docs = DocumentModel.get_by_stage(stage_id, conn)
        self.table.setRowCount(len(docs))

        for i, doc in enumerate(docs):
            # 문서명
            name_item = QTableWidgetItem(doc["name"])
            name_item.setData(Qt.UserRole, doc["id"])
            self.table.setItem(i, 0, name_item)

            # 상태 (배지)
            status = doc["status"]
            status_item = QTableWidgetItem(f"  {status}  ")
            color = STATUS_COLORS.get(status, "#8E8E93")
            status_item.setForeground(QColor("white"))
            status_item.setBackground(QColor(color))
            self.table.setItem(i, 1, status_item)

            # 검토자
            reviewer_item = QTableWidgetItem(doc["reviewer"] or "-")
            self.table.setItem(i, 2, reviewer_item)

            # 액션 버튼
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)

            edit_btn = QPushButton("Edit")
            edit_btn.setMaximumWidth(60)
            edit_btn.setProperty("secondary", True)
            edit_btn.clicked.connect(lambda _, d=doc["id"]: self._edit_document(d))
            btn_layout.addWidget(edit_btn)

            md_btn = QPushButton("Export MD")
            md_btn.setMaximumWidth(80)
            md_btn.setProperty("secondary", True)
            md_btn.clicked.connect(lambda _, d=doc["id"]: self._export_md(d))
            btn_layout.addWidget(md_btn)

            html_btn = QPushButton("Export HTML")
            html_btn.setMaximumWidth(90)
            html_btn.setProperty("secondary", True)
            html_btn.clicked.connect(lambda _, d=doc["id"]: self._export_html(d))
            btn_layout.addWidget(html_btn)

            self.table.setCellWidget(i, 3, btn_widget)

        if should_close:
            conn.close()

    def _save_content(self):
        """Save the content editor text to the selected document."""
        if not self._selected_doc_id:
            QMessageBox.warning(
                self, "No Document Selected",
                "Please select a document first.\n문서를 먼저 선택해주세요."
            )
            return
        content = self.content_edit.toPlainText()
        try:
            DocumentModel.update(self._selected_doc_id, content=content)
            QMessageBox.information(
                self, "Saved / 저장됨",
                "Document content saved successfully.\n문서 내용이 저장되었습니다."
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save content:\n{e}")

    def _on_cell_clicked(self, row, col):
        """문서 선택 시 내용을 편집기에 로드"""
        item = self.table.item(row, 0)
        if item:
            doc_id = item.data(Qt.UserRole)
            doc = DocumentModel.get_by_id(doc_id)
            if doc:
                self._selected_doc_id = doc_id
                self.content_edit.setPlainText(doc["content"] or "")

    def _export_md(self, doc_id):
        """Export document as Markdown."""
        from src.services.export_service import export_to_markdown
        path, _ = QFileDialog.getSaveFileName(
            self, "Export as Markdown", "", "Markdown Files (*.md);;All Files (*)"
        )
        if path:
            try:
                export_to_markdown(doc_id, path)
                QMessageBox.information(self, "Export", f"Exported to:\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))

    def _export_html(self, doc_id):
        """Export document as HTML."""
        from src.services.export_service import export_to_html
        path, _ = QFileDialog.getSaveFileName(
            self, "Export as HTML", "", "HTML Files (*.html);;All Files (*)"
        )
        if path:
            try:
                export_to_html(doc_id, path)
                QMessageBox.information(self, "Export", f"Exported to:\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))

    def _load_template_content(self, template_type):
        """Load template content based on the stage's SWE level or template_type."""
        from src.services.export_service import _TEMPLATE_MAP, _TEMPLATES_DIR
        from src.models.stage import StageModel
        from src.models.project import ProjectModel
        from src.models.oem import OemModel

        # Try template_type first, then fall back to SWE level
        filename = _TEMPLATE_MAP.get(template_type)
        if not filename and self.stage_id:
            stage = StageModel.get_by_id(self.stage_id)
            if stage:
                filename = _TEMPLATE_MAP.get(stage["swe_level"])

        if not filename:
            return ""

        path = os.path.join(_TEMPLATES_DIR, filename)
        if not os.path.isfile(path):
            return ""

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Fill placeholders
        project_name = ""
        oem_name = ""
        if self.stage_id:
            stage = StageModel.get_by_id(self.stage_id)
            if stage:
                project = ProjectModel.get_by_id(stage["project_id"])
                if project:
                    project_name = project["name"]
                    oem = OemModel.get_by_id(project["oem_id"])
                    if oem:
                        oem_name = oem["name"]

        content = content.replace("{project_name}", project_name)
        content = content.replace("{oem_name}", oem_name)
        content = content.replace("{date}", str(date.today()))
        return content

    def _add_document(self):
        if not self.stage_id:
            return
        dialog = DocumentDialog(self, stage_id=self.stage_id)
        if dialog.exec_():
            data = dialog.get_data()
            try:
                # Auto-load template content for new documents
                template_type = data.get("template_type", "")
                if template_type:
                    template_content = self._load_template_content(template_type)
                    if template_content:
                        data["content"] = template_content
                DocumentModel.create(self.stage_id, **data)
                self.load_stage(self.stage_id)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to create document:\n{e}")

    def _edit_document(self, doc_id):
        doc = DocumentModel.get_by_id(doc_id)
        if not doc:
            return
        dialog = DocumentDialog(self, doc)
        if dialog.exec_():
            data = dialog.get_data()
            DocumentModel.update(doc_id, **data)
            self.load_stage(self.stage_id)


class DocumentDialog(QDialog):
    def __init__(self, parent=None, doc=None, stage_id=None):
        super().__init__(parent)
        self.setWindowTitle("Document / 문서" if not doc else "Edit Document / 문서 편집")
        self.setMinimumWidth(400)
        self.doc = doc
        self.stage_id = stage_id
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Document name / 문서명")
        layout.addRow("Name / 이름:", self.name_edit)

        self.template_edit = QLineEdit()
        self.template_edit.setPlaceholderText("e.g., srs, sad, sdd")
        layout.addRow("Template ID:", self.template_edit)

        self.status_combo = QComboBox()
        self.status_combo.addItems(DocumentStatus.ALL)
        layout.addRow("Status / 상태:", self.status_combo)

        self.reviewer_edit = QLineEdit()
        layout.addRow("Reviewer / 검토자:", self.reviewer_edit)

        self.notes_edit = QLineEdit()
        layout.addRow("Notes / 메모:", self.notes_edit)

        # 버튼
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save / 저장")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel / 취소")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)

        if self.doc:
            self.name_edit.setText(self.doc["name"])
            self.template_edit.setText(self.doc["template_type"] or "")
            idx = self.status_combo.findText(self.doc["status"])
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)
            self.reviewer_edit.setText(self.doc["reviewer"] or "")
            self.notes_edit.setText(self.doc["notes"] or "")
        elif self.stage_id:
            # Auto-fill name with generated ID for new documents
            try:
                auto_id = DocumentModel.get_next_id(self.stage_id)
                self.name_edit.setText(auto_id)
            except Exception:
                pass

    def get_data(self):
        return {
            "name": self.name_edit.text(),
            "template_type": self.template_edit.text(),
            "status": self.status_combo.currentText(),
            "reviewer": self.reviewer_edit.text(),
            "notes": self.notes_edit.text(),
        }
