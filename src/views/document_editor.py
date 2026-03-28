"""문서 편집기 - 아이템 기반, 테이블 직접 편집 + 더블클릭 팝업 + 자동 저장"""
import json
import os
from datetime import date

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QPushButton, QComboBox,
    QHeaderView, QDialog, QLineEdit, QFormLayout, QTextEdit,
    QFileDialog, QMessageBox, QSplitter, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont

from src.models.document import DocumentModel
from src.models.database import get_connection
from src.utils.constants import DocumentStatus, STATUS_COLORS
from src.utils.styles import get_user_name

# SWE 단계별 아이템 스키마
ITEM_SCHEMAS = {
    "SWE.1": {
        "prefix": "REQ", "label": "Requirement",
        "columns": ["ID", "Requirement / 요구사항", "Priority", "Verification"],
        "fields": [
            {"key": "requirement", "label": "Requirement / 요구사항", "type": "text", "col": 1},
            {"key": "priority", "label": "Priority / 우선순위", "type": "combo", "options": ["High", "Medium", "Low"], "col": 2},
            {"key": "verification", "label": "Verification / 검증방법", "type": "combo", "options": ["Test", "Review", "Analysis", "Inspection"], "col": 3},
            {"key": "notes", "label": "Notes / 비고", "type": "multiline"},
        ],
    },
    "SWE.2": {
        "prefix": "CMP", "label": "Component",
        "columns": ["ID", "Component / 컴포넌트", "Responsibility / 역할", "Input", "Output"],
        "fields": [
            {"key": "component", "label": "Component / 컴포넌트명", "type": "text", "col": 1},
            {"key": "responsibility", "label": "Responsibility / 역할", "type": "text", "col": 2},
            {"key": "input", "label": "Input / 입력", "type": "text", "col": 3},
            {"key": "output", "label": "Output / 출력", "type": "text", "col": 4},
            {"key": "notes", "label": "Notes / 비고", "type": "multiline"},
        ],
    },
    "SWE.3": {
        "prefix": "FUN", "label": "Function",
        "columns": ["ID", "Function / 함수", "Input", "Output"],
        "fields": [
            {"key": "function", "label": "Function / 함수명", "type": "text", "col": 1},
            {"key": "input", "label": "Input / 입력", "type": "text", "col": 2},
            {"key": "output", "label": "Output / 출력", "type": "text", "col": 3},
            {"key": "description", "label": "Description / 설명", "type": "multiline"},
            {"key": "notes", "label": "Notes / 비고", "type": "multiline"},
        ],
    },
    "SWE.4": {
        "prefix": "UT", "label": "Unit Test",
        "columns": ["ID", "Function", "Test Description", "Result"],
        "fields": [
            {"key": "function", "label": "Function / 대상 함수", "type": "text", "col": 1},
            {"key": "test_desc", "label": "Test Description / 시험 내용", "type": "text", "col": 2},
            {"key": "expected", "label": "Expected / 기대값", "type": "text"},
            {"key": "actual", "label": "Actual / 실제값", "type": "text"},
            {"key": "result", "label": "Result / 결과", "type": "combo", "options": ["Pass", "Fail", "Blocked", "N/E"], "col": 3},
            {"key": "notes", "label": "Notes / 비고", "type": "multiline"},
        ],
    },
    "SWE.5": {
        "prefix": "IT", "label": "Integration Test",
        "columns": ["ID", "Interface", "Description", "Result"],
        "fields": [
            {"key": "interface", "label": "Interface / 인터페이스", "type": "text", "col": 1},
            {"key": "test_desc", "label": "Description / 시험 내용", "type": "text", "col": 2},
            {"key": "expected", "label": "Expected / 기대값", "type": "text"},
            {"key": "actual", "label": "Actual / 실제값", "type": "text"},
            {"key": "result", "label": "Result / 결과", "type": "combo", "options": ["Pass", "Fail", "Blocked", "N/E"], "col": 3},
            {"key": "notes", "label": "Notes / 비고", "type": "multiline"},
        ],
    },
    "SWE.6": {
        "prefix": "QT", "label": "Qualification Test",
        "columns": ["ID", "Req ID", "Test Description", "Result"],
        "fields": [
            {"key": "req_id", "label": "Requirement ID / 요구사항 ID", "type": "text", "col": 1},
            {"key": "test_desc", "label": "Test Description / 시험 내용", "type": "text", "col": 2},
            {"key": "expected", "label": "Expected / 기대값", "type": "text"},
            {"key": "actual", "label": "Actual / 실제값", "type": "text"},
            {"key": "result", "label": "Result / 결과", "type": "combo", "options": ["Pass", "Fail", "Blocked", "N/E"], "col": 3},
            {"key": "notes", "label": "Notes / 비고", "type": "multiline"},
        ],
    },
}


def _get_schema(swe_level):
    return ITEM_SCHEMAS.get(swe_level, ITEM_SCHEMAS["SWE.1"])


def _parse_items(content):
    if not content or not content.strip():
        return []
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, TypeError):
        pass
    return []


class ItemEditDialog(QDialog):
    """더블클릭 시 나타나는 아이템 편집 팝업"""

    def __init__(self, item, schema, parent=None):
        super().__init__(parent)
        self.item = dict(item)  # 복사본
        self.schema = schema
        self.setWindowTitle(f"Edit {item.get('id', '')}")
        self.setMinimumWidth(500)
        self._widgets = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 16, 20, 16)

        # ID (읽기전용)
        id_lbl = QLineEdit(self.item.get("id", ""))
        id_lbl.setReadOnly(True)
        id_lbl.setStyleSheet("background:#F2F2F7; color:#8E8E93; border-radius:6px; padding:6px;")
        layout.addRow("ID:", id_lbl)

        for field in self.schema["fields"]:
            key = field["key"]
            label = field["label"]
            ftype = field["type"]
            value = str(self.item.get(key, ""))

            if ftype == "text":
                w = QLineEdit(value)
                w.setStyleSheet("border:1px solid #D1D1D6; border-radius:6px; padding:6px;")
            elif ftype == "multiline":
                w = QTextEdit()
                w.setPlainText(value)
                w.setMaximumHeight(80)
                w.setStyleSheet("border:1px solid #D1D1D6; border-radius:6px; padding:6px;")
            elif ftype == "combo":
                w = QComboBox()
                w.addItems(field.get("options", []))
                idx = w.findText(value)
                if idx >= 0:
                    w.setCurrentIndex(idx)
            else:
                w = QLineEdit(value)

            layout.addRow(f"{label}:", w)
            self._widgets[key] = (ftype, w)

        # 버튼
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_item(self):
        for key, (ftype, w) in self._widgets.items():
            if ftype == "text":
                self.item[key] = w.text()
            elif ftype == "multiline":
                self.item[key] = w.toPlainText()
            elif ftype == "combo":
                self.item[key] = w.currentText()
        return self.item


class DocumentEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stage_id = None
        self._doc_id = None
        self._swe_level = "SWE.1"
        self._items = []
        self._auto_save_timer = QTimer()
        self._auto_save_timer.setSingleShot(True)
        self._auto_save_timer.setInterval(800)
        self._auto_save_timer.timeout.connect(self._auto_save)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 헤더
        header = QHBoxLayout()
        self.doc_title = QLabel("Select a stage")
        self.doc_title.setStyleSheet("font-size:15px; font-weight:600; color:#1C1C1E;")
        header.addWidget(self.doc_title)
        header.addStretch()

        self.status_label = QLabel("")
        header.addWidget(self.status_label)

        btn_export = QPushButton("Export")
        btn_export.setProperty("secondary", True)
        btn_export.setMaximumWidth(80)
        btn_export.clicked.connect(self._export_md)
        header.addWidget(btn_export)

        layout.addLayout(header)

        # + Add 버튼
        add_row = QHBoxLayout()
        self.btn_add = QPushButton("+ Add")
        self.btn_add.setMaximumWidth(100)
        self.btn_add.clicked.connect(self._add_item)
        add_row.addWidget(self.btn_add)
        add_row.addStretch()
        self.count_label = QLabel("0 items")
        self.count_label.setStyleSheet("color:#8E8E93; font-size:12px;")
        add_row.addWidget(self.count_label)
        self.save_indicator = QLabel("")
        self.save_indicator.setStyleSheet("color:#34C759; font-size:11px;")
        add_row.addWidget(self.save_indicator)
        layout.addLayout(add_row)

        # 아이템 테이블 (직접 편집 + 수평 스크롤)
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setWordWrap(True)
        self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.table.setStyleSheet("""
            QTableWidget { border:1px solid #E5E5EA; border-radius:8px; font-size:13px; }
            QTableWidget::item { padding:6px 10px; }
            QTableWidget::item:selected { background:#007AFF; color:white; }
        """)
        self.table.cellChanged.connect(self._on_cell_changed)
        self.table.cellDoubleClicked.connect(self._on_double_click)
        self.table.currentCellChanged.connect(self._on_row_changed)
        layout.addWidget(self.table)

        # 선택된 아이템의 상세 노트 영역 (노트앱 스타일)
        self.notes_frame = QFrame()
        self.notes_frame.setStyleSheet(
            "QFrame { background:#FFFFFF; border:1px solid #E5E5EA; border-radius:8px; }"
        )
        notes_layout = QVBoxLayout(self.notes_frame)
        notes_layout.setContentsMargins(12, 8, 12, 8)
        notes_layout.setSpacing(4)

        self.notes_title = QLabel("Notes / 상세 내용")
        self.notes_title.setStyleSheet("font-weight:600; color:#3A3A3C; font-size:13px; border:none;")
        notes_layout.addWidget(self.notes_title)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText(
            "Write detailed content here...\n"
            "요구사항 상세 내용, 배경, 제약사항 등을 자유롭게 작성하세요.\n\n"
            "Example:\n"
            "- 조향각 센서는 SPI 인터페이스로 5ms 주기 읽기\n"
            "- 유효 범위: ±720°, 분해능: 0.1°\n"
            "- 센서 고장 시 최후 유효값을 3 cycle 유지"
        )
        self.notes_edit.setStyleSheet(
            "QTextEdit { border:none; font-size:13px; line-height:1.6; background:transparent; }"
        )
        self.notes_edit.setMinimumHeight(120)
        self.notes_edit.textChanged.connect(self._on_notes_changed)
        notes_layout.addWidget(self.notes_edit)

        layout.addWidget(self.notes_frame)

    def load_stage(self, stage_id, conn=None):
        self.stage_id = stage_id
        should_close = conn is None
        if conn is None:
            conn = get_connection()

        from src.models.stage import StageModel
        stage = StageModel.get_by_id(stage_id, conn)
        if stage:
            self._swe_level = stage["swe_level"]

        docs = DocumentModel.get_by_stage(stage_id, conn)
        if docs:
            doc = docs[0]
            self._doc_id = doc["id"]
            self.doc_title.setText(f"{self._swe_level}: {doc['name']}")
            status = doc["status"]
            color = STATUS_COLORS.get(status, "#8E8E93")
            self.status_label.setText(f"  {status}  ")
            self.status_label.setStyleSheet(
                f"background:{color}; color:white; padding:3px 10px; border-radius:8px; font-size:11px;"
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

        schema = _get_schema(self._swe_level)
        self.btn_add.setText(f"+ Add {schema['prefix']}")
        self._refresh_table()
        self.notes_edit.blockSignals(True)
        self.notes_edit.clear()
        self.notes_title.setText("Notes / 상세 내용 — select an item")
        self.notes_edit.blockSignals(False)

    def _refresh_table(self):
        self.table.blockSignals(True)
        schema = _get_schema(self._swe_level)
        cols = schema["columns"] + [""]  # 마지막 열 = 삭제 버튼

        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        # 모든 컬럼을 내용에 맞게 자동 확장 (ResizeToContents)
        # 스크롤로 넘치는 부분 볼 수 있음
        for i in range(len(cols) - 1):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(len(cols) - 1, QHeaderView.Fixed)
        self.table.setColumnWidth(len(cols) - 1, 40)
        # 최소 컬럼 폭 설정
        self.table.horizontalHeader().setMinimumSectionSize(120)

        self.table.setRowCount(len(self._items))

        for r, item in enumerate(self._items):
            # ID (읽기전용)
            id_item = QTableWidgetItem(item.get("id", ""))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            id_item.setForeground(QColor("#8E8E93"))
            self.table.setItem(r, 0, id_item)

            # 테이블에 표시되는 필드들 (직접 편집 가능 + 툴팁)
            fields = schema["fields"]
            for f in fields:
                if "col" in f:
                    c = f["col"]
                    val = str(item.get(f["key"], ""))
                    cell = QTableWidgetItem(val)
                    cell.setToolTip(val)  # 마우스 오버 시 전체 내용 표시
                    self.table.setItem(r, c, cell)

            # 삭제 버튼
            del_btn = QPushButton("x")
            del_btn.setStyleSheet(
                "color:#FF3B30; background:transparent; border:none; font-weight:bold; font-size:14px;"
            )
            del_btn.setMaximumWidth(30)
            del_btn.clicked.connect(lambda _, row=r: self._delete_item(row))
            self.table.setCellWidget(r, len(cols) - 1, del_btn)

        # 행 높이 조절 (내용에 맞게)
        for r in range(len(self._items)):
            self.table.setRowHeight(r, 40)
        self.count_label.setText(f"{len(self._items)} items")
        self.table.blockSignals(False)

    def _on_row_changed(self, row, col, prev_row, prev_col):
        """행 변경 시 노트 영역 업데이트"""
        if row < 0 or row >= len(self._items):
            self.notes_edit.blockSignals(True)
            self.notes_edit.clear()
            self.notes_title.setText("Notes / 상세 내용")
            self.notes_edit.blockSignals(False)
            return

        item = self._items[row]
        item_id = item.get("id", "")
        self.notes_title.setText(f"Notes: {item_id}")
        self.notes_edit.blockSignals(True)
        self.notes_edit.setPlainText(item.get("notes", ""))
        self.notes_edit.blockSignals(False)

    def _on_notes_changed(self):
        """노트 편집 시 아이템에 반영 + 자동 저장"""
        row = self.table.currentRow()
        if row < 0 or row >= len(self._items):
            return
        self._items[row]["notes"] = self.notes_edit.toPlainText()
        self.save_indicator.setText("Saving...")
        self.save_indicator.setStyleSheet("color:#FF9500; font-size:11px;")
        self._auto_save_timer.start()

    def _on_cell_changed(self, row, col):
        """셀 편집 시 자동 저장 (800ms 디바운스)"""
        if row < 0 or row >= len(self._items) or col == 0:
            return

        schema = _get_schema(self._swe_level)
        # 컬럼 → 필드 키 매핑
        for f in schema["fields"]:
            if f.get("col") == col:
                cell = self.table.item(row, col)
                if cell:
                    self._items[row][f["key"]] = cell.text()
                break

        self.save_indicator.setText("Saving...")
        self.save_indicator.setStyleSheet("color:#FF9500; font-size:11px;")
        self._auto_save_timer.start()

    def _on_double_click(self, row, col):
        """더블클릭 → 편집 팝업"""
        if row < 0 or row >= len(self._items):
            return

        schema = _get_schema(self._swe_level)
        dialog = ItemEditDialog(self._items[row], schema, self)
        if dialog.exec_() == QDialog.Accepted:
            self._items[row] = dialog.get_item()
            self._refresh_table()
            self._auto_save()

    def _add_item(self):
        if not self._doc_id:
            return
        schema = _get_schema(self._swe_level)
        swe_num = self._swe_level.replace("SWE.", "")
        next_num = len(self._items) + 1
        new_id = f"SWE{swe_num}-{schema['prefix']}-{next_num:03d}"

        new_item = {"id": new_id}
        for f in schema["fields"]:
            new_item[f["key"]] = ""

        self._items.append(new_item)
        self._refresh_table()
        self._auto_save()

        # 새 행 선택
        self.table.selectRow(len(self._items) - 1)

    def _delete_item(self, row):
        if row < 0 or row >= len(self._items):
            return
        item_id = self._items[row].get("id", "")
        reply = QMessageBox.question(self, "Delete", f"Delete {item_id}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._items.pop(row)
            self._refresh_table()
            self._auto_save()

    def _auto_save(self):
        """DB에 자동 저장"""
        if not self._doc_id:
            return
        content = json.dumps(self._items, ensure_ascii=False, indent=2)
        try:
            DocumentModel.update(self._doc_id, content=content)
            self.save_indicator.setText("Saved")
            self.save_indicator.setStyleSheet("color:#34C759; font-size:11px;")
        except Exception:
            self.save_indicator.setText("Error")
            self.save_indicator.setStyleSheet("color:#FF3B30; font-size:11px;")

    def _export_md(self):
        if not self._doc_id:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export", "", "Markdown (*.md);;HTML (*.html)")
        if not path:
            return
        try:
            if path.endswith(".html"):
                from src.services.export_service import export_to_html
                export_to_html(self._doc_id, path)
            else:
                from src.services.export_service import export_to_markdown
                export_to_markdown(self._doc_id, path)
            QMessageBox.information(self, "Export", f"Exported:\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
