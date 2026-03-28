"""추적성 상세 뷰 - 항목 레벨 추적성 (QTableWidget 기반)"""
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

from src.models.database import get_connection
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.traceability import TraceabilityModel
from src.utils.constants import SWE_STAGES, LinkType


class TraceabilityDetailDialog(QDialog):
    """두 단계 사이의 항목 레벨 추적성 상세 뷰"""

    def __init__(self, stage_id_1, stage_id_2, parent=None):
        super().__init__(parent)
        self.stage_id_1 = stage_id_1
        self.stage_id_2 = stage_id_2
        self.setWindowTitle("Traceability Detail / 추적성 상세")
        self.setMinimumSize(800, 500)
        self.resize(900, 600)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        self.header_label = QLabel()
        self.header_label.setProperty("heading", True)
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.header_label.setFont(font)
        layout.addWidget(self.header_label)

        self.doc_label = QLabel()
        layout.addWidget(self.doc_label)

        self.summary_label = QLabel()
        self.summary_label.setProperty("caption", True)
        layout.addWidget(self.summary_label)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        layout.addWidget(sep)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Source Item", "Link Type", "Target Item", "Del"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setColumnWidth(3, 50)
        layout.addWidget(self.table, 1)

        # Add Link section
        add_group = QGroupBox("Add Link")
        add_layout = QHBoxLayout(add_group)
        add_layout.setSpacing(8)

        add_layout.addWidget(QLabel("Source:"))
        self.source_combo = QComboBox()
        self.source_combo.setMinimumWidth(160)
        add_layout.addWidget(self.source_combo)

        add_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(LinkType.ALL)
        add_layout.addWidget(self.type_combo)

        add_layout.addWidget(QLabel("Target:"))
        self.target_combo = QComboBox()
        self.target_combo.setMinimumWidth(160)
        add_layout.addWidget(self.target_combo)

        self.btn_add = QPushButton("Add Link")
        self.btn_add.clicked.connect(self._add_link)
        add_layout.addWidget(self.btn_add)

        layout.addWidget(add_group)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_close = QPushButton("Close / 닫기")
        self.btn_close.setProperty("secondary", True)
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

    def _get_item_ids_from_doc(self, doc):
        """Parse item IDs from document JSON content."""
        try:
            content = doc["content"] or ""
        except (KeyError, TypeError):
            content = ""
        if not content:
            return []
        try:
            items = json.loads(content)
            return [item.get("id", "") for item in items if isinstance(item, dict) and item.get("id")]
        except (json.JSONDecodeError, TypeError):
            return []

    def _load_data(self):
        conn = get_connection()

        stage_1 = StageModel.get_by_id(self.stage_id_1, conn)
        stage_2 = StageModel.get_by_id(self.stage_id_2, conn)

        if not stage_1 or not stage_2:
            conn.close()
            return

        swe_1 = stage_1["swe_level"]
        swe_2 = stage_2["swe_level"]

        docs_1 = DocumentModel.get_by_stage(self.stage_id_1, conn)
        docs_2 = DocumentModel.get_by_stage(self.stage_id_2, conn)
        links = TraceabilityModel.get_between_stages(self.stage_id_1, self.stage_id_2, conn)

        # Document names for display
        doc_name_1 = docs_1[0]["name"] if docs_1 else "N/A"
        doc_name_2 = docs_2[0]["name"] if docs_2 else "N/A"

        # Collect item IDs from all documents per stage
        source_items = []
        source_doc_map = {}  # item_id -> doc_id
        for doc in docs_1:
            ids = self._get_item_ids_from_doc(doc)
            for item_id in ids:
                source_items.append(item_id)
                source_doc_map[item_id] = doc["id"]

        target_items = []
        target_doc_map = {}
        for doc in docs_2:
            ids = self._get_item_ids_from_doc(doc)
            for item_id in ids:
                target_items.append(item_id)
                target_doc_map[item_id] = doc["id"]

        # Coverage: count source items that have at least one link
        linked_source_items = set()
        for link in links:
            try:
                src_item = link["source_item_id"]
            except (KeyError, IndexError):
                src_item = ""
            if src_item:
                linked_source_items.add(src_item)

        total_source = len(source_items) if source_items else max(len(docs_1), 1)
        covered = len(linked_source_items) if linked_source_items else len(links)
        coverage_pct = int(covered / total_source * 100) if total_source > 0 else 0

        # Header
        self.header_label.setText(
            f"Traceability: {swe_1} \u2194 {swe_2}"
        )
        self.doc_label.setText(
            f"Documents: {doc_name_1} \u2194 {doc_name_2}"
        )
        self.summary_label.setText(
            f"Links: {len(links)}  |  Coverage: {coverage_pct}%"
        )

        # Populate table
        self.table.setRowCount(len(links))
        self._link_ids = []
        for row_idx, link in enumerate(links):
            try:
                src_item = link["source_item_id"]
            except (KeyError, IndexError):
                src_item = ""
            try:
                tgt_item = link["target_item_id"]
            except (KeyError, IndexError):
                tgt_item = ""

            source_display = src_item if src_item else link["source_name"]
            target_display = tgt_item if tgt_item else link["target_name"]
            link_type = link["link_type"]
            link_id = link["id"]
            self._link_ids.append(link_id)

            src_cell = QTableWidgetItem(source_display)
            src_cell.setToolTip(f"Doc: {link['source_name']}")
            self.table.setItem(row_idx, 0, src_cell)

            type_cell = QTableWidgetItem(link_type)
            type_cell.setTextAlignment(Qt.AlignCenter)
            color_map = {
                LinkType.DERIVES: QColor("#007AFF"),
                LinkType.VERIFIES: QColor("#34C759"),
                LinkType.SATISFIES: QColor("#FF9500"),
            }
            type_cell.setForeground(color_map.get(link_type, QColor("#8E8E93")))
            self.table.setItem(row_idx, 1, type_cell)

            tgt_cell = QTableWidgetItem(target_display)
            tgt_cell.setToolTip(f"Doc: {link['target_name']}")
            self.table.setItem(row_idx, 2, tgt_cell)

            del_btn = QPushButton("x")
            del_btn.setFixedSize(30, 24)
            del_btn.setStyleSheet("color: #FF3B30; font-weight: bold; border: none;")
            del_btn.clicked.connect(lambda checked, lid=link_id: self._delete_link(lid))
            self.table.setCellWidget(row_idx, 3, del_btn)

        # Populate combo boxes
        self.source_combo.clear()
        self.target_combo.clear()

        # Store doc maps for use in _add_link
        self._source_doc_map = source_doc_map
        self._target_doc_map = target_doc_map
        self._docs_1 = docs_1
        self._docs_2 = docs_2

        if source_items:
            for item_id in source_items:
                self.source_combo.addItem(item_id, item_id)
        elif docs_1:
            for doc in docs_1:
                self.source_combo.addItem(doc["name"], doc["name"])

        if target_items:
            for item_id in target_items:
                self.target_combo.addItem(item_id, item_id)
        elif docs_2:
            for doc in docs_2:
                self.target_combo.addItem(doc["name"], doc["name"])

        conn.close()

    def _delete_link(self, link_id):
        """Delete a traceability link and refresh."""
        conn = get_connection()
        try:
            TraceabilityModel.delete(link_id, conn=conn)
        finally:
            conn.close()
        self._load_data()

    def _add_link(self):
        """Add a new traceability link from the combo selections."""
        source_val = self.source_combo.currentData()
        target_val = self.target_combo.currentData()
        link_type = self.type_combo.currentText()

        if not source_val or not target_val:
            return

        # Resolve document IDs
        source_doc_id = self._source_doc_map.get(source_val)
        target_doc_id = self._target_doc_map.get(target_val)

        # If combos show document names (no item IDs), resolve from docs
        if source_doc_id is None and self._docs_1:
            for doc in self._docs_1:
                if doc["name"] == source_val:
                    source_doc_id = doc["id"]
                    break
            if source_doc_id is None:
                source_doc_id = self._docs_1[0]["id"]
            source_item_id = ""
        else:
            source_item_id = source_val if source_doc_id else ""
            if source_doc_id is None and self._docs_1:
                source_doc_id = self._docs_1[0]["id"]

        if target_doc_id is None and self._docs_2:
            for doc in self._docs_2:
                if doc["name"] == target_val:
                    target_doc_id = doc["id"]
                    break
            if target_doc_id is None:
                target_doc_id = self._docs_2[0]["id"]
            target_item_id = ""
        else:
            target_item_id = target_val if target_doc_id else ""
            if target_doc_id is None and self._docs_2:
                target_doc_id = self._docs_2[0]["id"]

        if source_doc_id is None or target_doc_id is None:
            return

        conn = get_connection()
        try:
            TraceabilityModel.create(
                source_doc_id,
                target_doc_id,
                link_type=link_type,
                source_item_id=source_item_id,
                target_item_id=target_item_id,
                conn=conn,
            )
        finally:
            conn.close()
        self._load_data()
