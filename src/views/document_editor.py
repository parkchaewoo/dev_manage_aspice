"""문서 편집기 - SWE 단계별 아이템 기반 편집"""
import json
import os
from datetime import date

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QPushButton, QComboBox,
    QHeaderView, QDialog, QLineEdit, QFormLayout, QTextEdit,
    QFileDialog, QMessageBox, QSplitter, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from src.models.document import DocumentModel
from src.models.database import get_connection
from src.utils.constants import DocumentStatus, STATUS_COLORS
from src.utils.styles import get_user_name


# SWE 단계별 아이템 스키마 정의
ITEM_SCHEMAS = {
    "SWE.1": {
        "prefix": "REQ",
        "label": "Requirement",
        "columns": ["ID", "Requirement / 요구사항", "Priority", "Verification"],
        "fields": [
            {"key": "requirement", "label": "Requirement / 요구사항", "type": "text"},
            {"key": "priority", "label": "Priority / 우선순위", "type": "combo", "options": ["High", "Medium", "Low"]},
            {"key": "verification", "label": "Verification / 검증방법", "type": "combo", "options": ["Test", "Review", "Analysis", "Inspection"]},
            {"key": "notes", "label": "Notes / 비고", "type": "text"},
        ],
    },
    "SWE.2": {
        "prefix": "CMP",
        "label": "Component",
        "columns": ["ID", "Component / 컴포넌트", "Responsibility / 역할", "Input", "Output"],
        "fields": [
            {"key": "component", "label": "Component Name / 컴포넌트명", "type": "text"},
            {"key": "responsibility", "label": "Responsibility / 역할", "type": "text"},
            {"key": "input", "label": "Input / 입력", "type": "text"},
            {"key": "output", "label": "Output / 출력", "type": "text"},
            {"key": "notes", "label": "Notes / 비고", "type": "text"},
        ],
    },
    "SWE.3": {
        "prefix": "FUN",
        "label": "Function",
        "columns": ["ID", "Function / 함수", "Input", "Output", "Description"],
        "fields": [
            {"key": "function", "label": "Function Name / 함수명", "type": "text"},
            {"key": "input", "label": "Input / 입력", "type": "text"},
            {"key": "output", "label": "Output / 출력", "type": "text"},
            {"key": "description", "label": "Description / 설명", "type": "multiline"},
            {"key": "notes", "label": "Notes / 비고", "type": "text"},
        ],
    },
    "SWE.4": {
        "prefix": "UT",
        "label": "Unit Test",
        "columns": ["ID", "Function", "Test Description", "Expected", "Result"],
        "fields": [
            {"key": "function", "label": "Function / 대상 함수", "type": "text"},
            {"key": "test_desc", "label": "Test Description / 시험 내용", "type": "text"},
            {"key": "expected", "label": "Expected / 기대값", "type": "text"},
            {"key": "actual", "label": "Actual / 실제값", "type": "text"},
            {"key": "result", "label": "Result / 결과", "type": "combo", "options": ["Pass", "Fail", "Blocked", "Not Executed"]},
            {"key": "notes", "label": "Notes / 비고", "type": "text"},
        ],
    },
    "SWE.5": {
        "prefix": "IT",
        "label": "Integration Test",
        "columns": ["ID", "Interface", "Description", "Expected", "Result"],
        "fields": [
            {"key": "interface", "label": "Interface / 인터페이스", "type": "text"},
            {"key": "test_desc", "label": "Test Description / 시험 내용", "type": "text"},
            {"key": "expected", "label": "Expected / 기대값", "type": "text"},
            {"key": "actual", "label": "Actual / 실제값", "type": "text"},
            {"key": "result", "label": "Result / 결과", "type": "combo", "options": ["Pass", "Fail", "Blocked", "Not Executed"]},
            {"key": "notes", "label": "Notes / 비고", "type": "text"},
        ],
    },
    "SWE.6": {
        "prefix": "QT",
        "label": "Qualification Test",
        "columns": ["ID", "Req ID", "Test Description", "Result"],
        "fields": [
            {"key": "req_id", "label": "Requirement ID / 요구사항 ID", "type": "text"},
            {"key": "test_desc", "label": "Test Description / 시험 내용", "type": "text"},
            {"key": "expected", "label": "Expected / 기대값", "type": "text"},
            {"key": "actual", "label": "Actual / 실제값", "type": "text"},
            {"key": "result", "label": "Result / 결과", "type": "combo", "options": ["Pass", "Fail", "Blocked", "Not Executed"]},
            {"key": "notes", "label": "Notes / 비고", "type": "text"},
        ],
    },
}


def _get_schema(swe_level):
    return ITEM_SCHEMAS.get(swe_level, ITEM_SCHEMAS["SWE.1"])


def _parse_items(content):
    """문서 content에서 아이템 리스트 파싱 (JSON 또는 빈 리스트)"""
    if not content or not content.strip():
        return []
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, TypeError):
        pass
    return []


def _items_to_json(items):
    return json.dumps(items, ensure_ascii=False, indent=2)


class DocumentEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stage_id = None
        self._doc_id = None
        self._swe_level = "SWE.1"
        self._items = []
        self._selected_row = -1
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 상단: 문서 제목 + 상태 + Export
        title_row = QHBoxLayout()
        self.doc_title = QLabel("Select a stage")
        self.doc_title.setStyleSheet("font-size:15px; font-weight:bold; color:#007AFF; padding:4px;")
        title_row.addWidget(self.doc_title)
        title_row.addStretch()

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("padding:4px 10px; border-radius:6px; font-size:12px;")
        title_row.addWidget(self.status_label)

        btn_export = QPushButton("Export MD")
        btn_export.setProperty("secondary", True)
        btn_export.setMaximumWidth(100)
        btn_export.clicked.connect(self._export_md)
        title_row.addWidget(btn_export)

        btn_export_html = QPushButton("Export HTML")
        btn_export_html.setProperty("secondary", True)
        btn_export_html.setMaximumWidth(110)
        btn_export_html.clicked.connect(self._export_html)
        title_row.addWidget(btn_export_html)

        layout.addLayout(title_row)

        # 상하 분할
        splitter = QSplitter(Qt.Vertical)

        # === 상단: 아이템 목록 ===
        top_panel = QWidget()
        top_layout = QVBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 4, 0, 0)
        top_layout.setSpacing(4)

        # + Add 버튼
        add_row = QHBoxLayout()
        self.btn_add = QPushButton("+ Add")
        self.btn_add.setMaximumWidth(100)
        self.btn_add.clicked.connect(self._add_item)
        add_row.addWidget(self.btn_add)
        add_row.addStretch()

        self.item_count_label = QLabel("0 items")
        self.item_count_label.setStyleSheet("color:#8E8E93;")
        add_row.addWidget(self.item_count_label)
        top_layout.addLayout(add_row)

        # 아이템 테이블
        self.item_table = QTableWidget()
        self.item_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.item_table.setAlternatingRowColors(True)
        self.item_table.verticalHeader().setVisible(False)
        self.item_table.cellClicked.connect(self._on_item_clicked)
        top_layout.addWidget(self.item_table)

        splitter.addWidget(top_panel)

        # === 하단: 상세 편집 폼 ===
        bottom_panel = QFrame()
        bottom_panel.setStyleSheet("QFrame { background:#FAFAFA; border-top:1px solid #E5E5EA; }")
        self.detail_layout = QVBoxLayout(bottom_panel)
        self.detail_layout.setContentsMargins(12, 8, 12, 8)
        self.detail_layout.setSpacing(6)

        self.detail_title = QLabel("Click an item above to edit / 위 항목을 클릭하여 편집")
        self.detail_title.setStyleSheet("font-weight:bold; color:#3A3A3C; font-size:14px;")
        self.detail_layout.addWidget(self.detail_title)

        # 폼 필드 컨테이너
        self.form_container = QWidget()
        self.form_layout = QFormLayout(self.form_container)
        self.form_layout.setSpacing(8)
        self.detail_layout.addWidget(self.form_container)

        # Save + Delete 버튼
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_delete = QPushButton("Delete Item")
        self.btn_delete.setProperty("danger", True)
        self.btn_delete.setMaximumWidth(120)
        self.btn_delete.clicked.connect(self._delete_item)
        btn_row.addWidget(self.btn_delete)

        self.btn_save = QPushButton("Save")
        self.btn_save.setMaximumWidth(100)
        self.btn_save.clicked.connect(self._save_item)
        btn_row.addWidget(self.btn_save)
        self.detail_layout.addLayout(btn_row)

        splitter.addWidget(bottom_panel)
        splitter.setSizes([300, 200])

        layout.addWidget(splitter)

    def load_stage(self, stage_id, conn=None):
        """단계의 문서 로드"""
        self.stage_id = stage_id
        should_close = conn is None
        if conn is None:
            conn = get_connection()

        # SWE 레벨 가져오기
        from src.models.stage import StageModel
        stage = StageModel.get_by_id(stage_id, conn)
        if stage:
            self._swe_level = stage["swe_level"]

        # 해당 단계의 첫 번째 문서 로드
        docs = DocumentModel.get_by_stage(stage_id, conn)
        if docs:
            doc = docs[0]
            self._doc_id = doc["id"]
            self.doc_title.setText(f"{self._swe_level}: {doc['name']}")

            status = doc["status"]
            color = STATUS_COLORS.get(status, "#8E8E93")
            self.status_label.setText(f"  {status}  ")
            self.status_label.setStyleSheet(
                f"background:{color}; color:white; padding:4px 10px; "
                f"border-radius:6px; font-size:12px;"
            )

            try:
                content = doc["content"] or ""
            except (IndexError, KeyError):
                content = ""
            self._items = _parse_items(content)
        else:
            self._doc_id = None
            self._items = []
            self.doc_title.setText(f"{self._swe_level}: No document")
            self.status_label.setText("")

        if should_close:
            conn.close()

        # UI 업데이트
        schema = _get_schema(self._swe_level)
        self.btn_add.setText(f"+ Add {schema['prefix']}")
        self._refresh_table()
        self._selected_row = -1
        self._clear_form()

    def _refresh_table(self):
        """아이템 테이블 새로고침"""
        schema = _get_schema(self._swe_level)
        cols = schema["columns"]

        self.item_table.setColumnCount(len(cols))
        self.item_table.setHorizontalHeaderLabels(cols)
        for i in range(len(cols)):
            if i == 0:
                self.item_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
            else:
                self.item_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.item_table.setRowCount(len(self._items))
        for r, item in enumerate(self._items):
            # ID
            id_item = QTableWidgetItem(item.get("id", ""))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.item_table.setItem(r, 0, id_item)

            # 나머지 컬럼 (필드 순서대로)
            fields = schema["fields"]
            for c in range(1, len(cols)):
                if c - 1 < len(fields):
                    key = fields[c - 1]["key"]
                    val = item.get(key, "")
                    cell = QTableWidgetItem(str(val)[:50])
                    cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
                    self.item_table.setItem(r, c, cell)

        self.item_count_label.setText(f"{len(self._items)} items")

    def _on_item_clicked(self, row, col):
        """아이템 클릭 → 하단 폼에 필드 표시"""
        if row < 0 or row >= len(self._items):
            return
        self._selected_row = row
        item = self._items[row]
        schema = _get_schema(self._swe_level)

        self.detail_title.setText(f"Edit: {item.get('id', '')}")
        self._build_form(schema, item)

    def _build_form(self, schema, item):
        """상세 편집 폼 생성"""
        # 기존 폼 제거
        while self.form_layout.count():
            child = self.form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._form_widgets = {}

        # ID (읽기 전용)
        id_edit = QLineEdit(item.get("id", ""))
        id_edit.setReadOnly(True)
        id_edit.setStyleSheet("background:#E5E5EA; color:#8E8E93;")
        self.form_layout.addRow("ID:", id_edit)

        # 각 필드
        for field in schema["fields"]:
            key = field["key"]
            label = field["label"]
            ftype = field["type"]
            value = item.get(key, "")

            if ftype == "text":
                w = QLineEdit(str(value))
                w.setPlaceholderText(f"Enter {label}")
            elif ftype == "multiline":
                w = QTextEdit()
                w.setPlainText(str(value))
                w.setMaximumHeight(80)
                w.setPlaceholderText(f"Enter {label}")
            elif ftype == "combo":
                w = QComboBox()
                w.addItems(field.get("options", []))
                idx = w.findText(str(value))
                if idx >= 0:
                    w.setCurrentIndex(idx)
            else:
                w = QLineEdit(str(value))

            self.form_layout.addRow(f"{label}:", w)
            self._form_widgets[key] = (ftype, w)

    def _clear_form(self):
        """폼 초기화"""
        while self.form_layout.count():
            child = self.form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._form_widgets = {}
        self.detail_title.setText("Click an item above to edit / 위 항목을 클릭하여 편집")

    def _add_item(self):
        """새 아이템 추가"""
        if not self._doc_id:
            return

        schema = _get_schema(self._swe_level)
        prefix = schema["prefix"]
        swe_num = self._swe_level.replace("SWE.", "")
        next_num = len(self._items) + 1
        new_id = f"SWE{swe_num}-{prefix}-{next_num:03d}"

        new_item = {"id": new_id}
        for field in schema["fields"]:
            new_item[field["key"]] = ""

        self._items.append(new_item)
        self._save_all_to_db()
        self._refresh_table()

        # 새 아이템 선택
        new_row = len(self._items) - 1
        self.item_table.selectRow(new_row)
        self._on_item_clicked(new_row, 0)

    def _save_item(self):
        """현재 편집 중인 아이템 저장"""
        if self._selected_row < 0 or self._selected_row >= len(self._items):
            return

        item = self._items[self._selected_row]
        for key, (ftype, widget) in self._form_widgets.items():
            if ftype == "text":
                item[key] = widget.text()
            elif ftype == "multiline":
                item[key] = widget.toPlainText()
            elif ftype == "combo":
                item[key] = widget.currentText()

        self._save_all_to_db()
        self._refresh_table()
        QMessageBox.information(self, "Saved", f"{item.get('id', '')} saved.")

    def _delete_item(self):
        """선택된 아이템 삭제"""
        if self._selected_row < 0 or self._selected_row >= len(self._items):
            return

        item = self._items[self._selected_row]
        reply = QMessageBox.question(
            self, "Delete", f"Delete {item.get('id', '')}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._items.pop(self._selected_row)
            self._save_all_to_db()
            self._refresh_table()
            self._selected_row = -1
            self._clear_form()

    def _save_all_to_db(self):
        """전체 아이템을 JSON으로 DB에 저장"""
        if not self._doc_id:
            return
        content = _items_to_json(self._items)

        conn = get_connection()
        try:
            # 버전 스냅샷
            old_doc = DocumentModel.get_by_id(self._doc_id, conn)
            if old_doc:
                try:
                    old_content = old_doc["content"] or ""
                except (IndexError, KeyError):
                    old_content = ""
                if old_content:
                    ver_count = conn.execute(
                        "SELECT COUNT(*) FROM document_versions WHERE document_id = ?",
                        (self._doc_id,)
                    ).fetchone()[0]
                    user = get_user_name() or "System"
                    conn.execute(
                        "INSERT INTO document_versions (document_id, version_number, content_snapshot, change_description, changed_by) VALUES (?,?,?,?,?)",
                        (self._doc_id, ver_count + 1, old_content, "Items updated", user)
                    )
                    conn.commit()

            DocumentModel.update(self._doc_id, content=content, conn=conn)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Save failed: {e}")
        finally:
            conn.close()

    def _export_md(self):
        """마크다운으로 내보내기"""
        if not self._doc_id:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Markdown", "", "Markdown (*.md)")
        if not path:
            return
        try:
            from src.services.export_service import export_to_markdown
            export_to_markdown(self._doc_id, path)
            QMessageBox.information(self, "Export", f"Exported to:\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _export_html(self):
        """HTML로 내보내기"""
        if not self._doc_id:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export HTML", "", "HTML (*.html)")
        if not path:
            return
        try:
            from src.services.export_service import export_to_html
            export_to_html(self._doc_id, path)
            QMessageBox.information(self, "Export", f"Exported to:\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
