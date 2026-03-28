"""추적성 교차 참조 매트릭스"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush

from src.models.database import get_connection
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.traceability import TraceabilityModel
from src.utils.constants import SWE_STAGES, VMODEL_PAIRS


class TraceabilityMatrixWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_id = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.title_label = QLabel("Traceability Matrix / 추적성 매트릭스")
        self.title_label.setProperty("heading", True)
        layout.addWidget(self.title_label)

        self.summary_label = QLabel()
        self.summary_label.setProperty("caption", True)
        layout.addWidget(self.summary_label)

        # 단계 레벨 매트릭스
        stage_frame = QFrame()
        stage_frame.setProperty("card", True)
        stage_layout = QVBoxLayout(stage_frame)

        stage_layout.addWidget(QLabel("Stage-Level Traceability / 단계 수준 추적성"))

        self.stage_table = QTableWidget()
        self.stage_table.setMinimumHeight(200)
        stage_layout.addWidget(self.stage_table)
        layout.addWidget(stage_frame)

        # 문서 레벨 매트릭스
        doc_frame = QFrame()
        doc_frame.setProperty("card", True)
        doc_layout = QVBoxLayout(doc_frame)

        doc_layout.addWidget(QLabel("Document-Level Traceability / 문서 수준 추적성"))

        self.doc_table = QTableWidget()
        self.doc_table.setMinimumHeight(300)
        doc_layout.addWidget(self.doc_table)
        layout.addWidget(doc_frame)

    def load_project(self, project_id):
        """프로젝트의 추적성 매트릭스 로드"""
        self.project_id = project_id
        conn = get_connection()

        stages = StageModel.get_by_project(project_id, conn)
        stage_map = {s["swe_level"]: s for s in stages}

        # --- 단계 레벨 매트릭스 ---
        swe_levels = sorted(stage_map.keys())
        n = len(swe_levels)
        self.stage_table.setRowCount(n)
        self.stage_table.setColumnCount(n + 1)

        headers = swe_levels + ["Coverage"]
        self.stage_table.setHorizontalHeaderLabels(headers)
        self.stage_table.setVerticalHeaderLabels(swe_levels)
        self.stage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        total_links = 0
        total_possible = 0

        for i, swe_i in enumerate(swe_levels):
            stage_i = stage_map[swe_i]
            row_links = 0
            row_total = 0

            for j, swe_j in enumerate(swe_levels):
                stage_j = stage_map[swe_j]

                if i == j:
                    item = QTableWidgetItem("-")
                    item.setBackground(QBrush(QColor("#F2F2F7")))
                    self.stage_table.setItem(i, j, item)
                    continue

                completeness = TraceabilityModel.get_completeness_for_pair(
                    stage_i["id"], stage_j["id"], conn
                )

                count = completeness["link_count"]
                pct = completeness["completeness_pct"]

                item = QTableWidgetItem(f"{count}")
                item.setTextAlignment(Qt.AlignCenter)

                # V-model 쌍이면 강조
                is_pair = (VMODEL_PAIRS.get(swe_i) == swe_j or
                          VMODEL_PAIRS.get(swe_j) == swe_i)

                if is_pair:
                    if pct >= 100:
                        item.setBackground(QBrush(QColor("#E8F5E9")))
                    elif pct > 0:
                        item.setBackground(QBrush(QColor("#FFF3E0")))
                    else:
                        item.setBackground(QBrush(QColor("#FFEBEE")))
                    row_total += 1
                    if count > 0:
                        row_links += 1

                self.stage_table.setItem(i, j, item)
                total_links += count

            # 커버리지 열
            cov = f"{row_links}/{row_total}" if row_total > 0 else "-"
            cov_item = QTableWidgetItem(cov)
            cov_item.setTextAlignment(Qt.AlignCenter)
            self.stage_table.setItem(i, n, cov_item)

        self.summary_label.setText(
            f"Total trace links: {total_links} / "
            f"전체 추적성 링크: {total_links}개"
        )

        # --- 문서 레벨 매트릭스 ---
        all_docs = []
        for stage in stages:
            docs = DocumentModel.get_by_stage(stage["id"], conn)
            for doc in docs:
                all_docs.append({
                    "id": doc["id"],
                    "name": doc["name"],
                    "swe": stage["swe_level"],
                    "stage_id": stage["id"],
                })

        nd = len(all_docs)
        self.doc_table.setRowCount(nd)
        self.doc_table.setColumnCount(nd)

        doc_labels = [f"{d['swe']}: {d['name'][:20]}" for d in all_docs]
        self.doc_table.setHorizontalHeaderLabels(doc_labels)
        self.doc_table.setVerticalHeaderLabels(doc_labels)

        # 모든 추적성 링크 수집
        all_links = set()
        for stage in stages:
            for doc in DocumentModel.get_by_stage(stage["id"], conn):
                links = TraceabilityModel.get_by_document(doc["id"], conn)
                for link in links:
                    all_links.add((link["source_document_id"], link["target_document_id"]))

        for i in range(nd):
            for j in range(nd):
                if i == j:
                    item = QTableWidgetItem("-")
                    item.setBackground(QBrush(QColor("#F2F2F7")))
                elif (all_docs[i]["id"], all_docs[j]["id"]) in all_links or \
                     (all_docs[j]["id"], all_docs[i]["id"]) in all_links:
                    item = QTableWidgetItem("✓")
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setForeground(QColor("#34C759"))
                    item.setBackground(QBrush(QColor("#E8F5E9")))
                else:
                    item = QTableWidgetItem("")
                self.doc_table.setItem(i, j, item)

        conn.close()
