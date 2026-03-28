"""추적성 상세 뷰 - 문서 레벨 다대다 연결 (드래그 앤 드롭 지원) + 항목 레벨 추적성"""
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QPushButton, QComboBox, QGraphicsLineItem
)
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF
from PyQt5.QtGui import QPen, QColor, QBrush, QFont, QPainter, QPainterPath

from src.models.database import get_connection
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.traceability import TraceabilityModel
from src.utils.constants import SWE_STAGES, STATUS_COLORS, DocumentStatus, LinkType


class DraggableDocCard(QGraphicsRectItem):
    """드래그 가능한 문서 카드 - 드래그로 추적성 링크 생성"""

    def __init__(self, x, y, w, h, doc_id, side, dialog, parent=None):
        super().__init__(x, y, w, h, parent)
        self.doc_id = doc_id
        self.side = side  # "left" or "right"
        self.dialog = dialog
        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)
        self._is_hover = False
        self._drag_line = None

    def hoverEnterEvent(self, event):
        """마우스 오버 시 하이라이트"""
        self._is_hover = True
        self.setPen(QPen(QColor("#0A84FF"), 3))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """마우스 떠날 때 원래 스타일 복원"""
        self._is_hover = False
        self.dialog._restore_card_pen(self)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        """드래그 시작"""
        if event.button() == Qt.LeftButton:
            self.dialog._drag_source = self
            center = self.rect().center() + self.pos()
            # Create temporary drag line
            self._drag_line = QGraphicsLineItem(
                QLineF(center, event.scenePos())
            )
            self._drag_line.setPen(QPen(QColor("#0A84FF"), 2, Qt.DashLine))
            self.scene().addItem(self._drag_line)
            # Highlight valid drop targets (opposite side cards)
            self.dialog._highlight_drop_targets(self.side)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """드래그 중 라인 업데이트"""
        if self._drag_line:
            center = self.rect().center() + self.pos()
            self._drag_line.setLine(QLineF(center, event.scenePos()))
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """드롭 - 타겟 카드 위에서 놓으면 링크 생성"""
        if self._drag_line:
            # Remove drag line
            self.scene().removeItem(self._drag_line)
            self._drag_line = None

            # Find card under drop point
            target = self.dialog._find_card_at(event.scenePos())
            if target and target is not self and target.side != self.side:
                # Create traceability link
                self.dialog._create_drag_link(self.doc_id, target.doc_id)

            # Reset highlights
            self.dialog._reset_highlights()
            self.dialog._drag_source = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class TraceabilityDetailDialog(QDialog):
    """두 단계 사이의 문서 레벨 추적성 상세 뷰"""

    def __init__(self, stage_id_1, stage_id_2, parent=None):
        super().__init__(parent)
        self.stage_id_1 = stage_id_1
        self.stage_id_2 = stage_id_2
        self._drag_source = None
        self._doc_cards = []  # list of DraggableDocCard
        self._card_original_pens = {}  # card -> original QPen
        self.setWindowTitle("Traceability Detail / 추적성 상세")
        self.setMinimumSize(800, 500)
        self.resize(900, 600)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 헤더
        self.header_label = QLabel()
        self.header_label.setProperty("heading", True)
        layout.addWidget(self.header_label)

        self.summary_label = QLabel()
        self.summary_label.setProperty("caption", True)
        layout.addWidget(self.summary_label)

        # 그래픽스 뷰
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setStyleSheet("background-color: #FAFAFA; border-radius: 8px;")
        layout.addWidget(self.view, 1)

        # 추가 버튼
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_add_link = QPushButton("+ Add Trace Link / 추적성 추가")
        self.btn_add_link.clicked.connect(self._add_link)
        btn_layout.addWidget(self.btn_add_link)

        self.btn_close = QPushButton("Close / 닫기")
        self.btn_close.setProperty("secondary", True)
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

    def _load_data(self):
        self.scene.clear()
        self._doc_cards = []
        self._card_original_pens = {}
        conn = get_connection()

        stage_1 = StageModel.get_by_id(self.stage_id_1, conn)
        stage_2 = StageModel.get_by_id(self.stage_id_2, conn)

        if not stage_1 or not stage_2:
            conn.close()
            return

        swe_1 = stage_1["swe_level"]
        swe_2 = stage_2["swe_level"]

        self.header_label.setText(
            f"{swe_1} ({SWE_STAGES[swe_1]['name_ko']})  ←→  "
            f"{swe_2} ({SWE_STAGES[swe_2]['name_ko']})"
        )

        docs_1 = DocumentModel.get_by_stage(self.stage_id_1, conn)
        docs_2 = DocumentModel.get_by_stage(self.stage_id_2, conn)
        links = TraceabilityModel.get_between_stages(self.stage_id_1, self.stage_id_2, conn)

        self.summary_label.setText(
            f"Documents: {len(docs_1)} + {len(docs_2)}  |  "
            f"Trace links: {len(links)}"
        )

        # 문서 카드 배치
        card_w, card_h = 200, 50
        left_x, right_x = 30, 500
        y_start = 30
        y_gap = 70

        # 좌측 단계 제목
        left_title = self.scene.addText(
            f"{swe_1}: {SWE_STAGES[swe_1]['name_ko']}",
            QFont("sans-serif", 11, QFont.Bold)
        )
        left_title.setDefaultTextColor(QColor("#007AFF"))
        left_title.setPos(left_x, 0)

        # 우측 단계 제목
        right_title = self.scene.addText(
            f"{swe_2}: {SWE_STAGES[swe_2]['name_ko']}",
            QFont("sans-serif", 11, QFont.Bold)
        )
        right_title.setDefaultTextColor(QColor("#007AFF"))
        right_title.setPos(right_x, 0)

        # 링크로 연결된 문서 ID 수집
        linked_source_ids = set()
        linked_target_ids = set()
        for link in links:
            linked_source_ids.add(link["source_document_id"])
            linked_target_ids.add(link["target_document_id"])

        # 좌측 문서 카드
        left_cards = {}
        for i, doc in enumerate(docs_1):
            y = y_start + i * y_gap
            is_linked = doc["id"] in linked_source_ids or doc["id"] in linked_target_ids
            item_count = self._get_item_count(doc)
            card = self._draw_doc_card(
                left_x, y, card_w, card_h,
                doc["name"], doc["status"], is_linked,
                doc_id=doc["id"], side="left", item_count=item_count
            )
            left_cards[doc["id"]] = (left_x + card_w, y + card_h / 2)

        # 우측 문서 카드
        right_cards = {}
        for i, doc in enumerate(docs_2):
            y = y_start + i * y_gap
            is_linked = doc["id"] in linked_source_ids or doc["id"] in linked_target_ids
            item_count = self._get_item_count(doc)
            card = self._draw_doc_card(
                right_x, y, card_w, card_h,
                doc["name"], doc["status"], is_linked,
                doc_id=doc["id"], side="right", item_count=item_count
            )
            right_cards[doc["id"]] = (right_x, y + card_h / 2)

        # 연결선 그리기
        for link in links:
            src_pos = left_cards.get(link["source_document_id"]) or right_cards.get(link["source_document_id"])
            dst_pos = right_cards.get(link["target_document_id"]) or left_cards.get(link["target_document_id"])

            if src_pos and dst_pos:
                color_map = {
                    LinkType.DERIVES: "#007AFF",
                    LinkType.VERIFIES: "#34C759",
                    LinkType.SATISFIES: "#FF9500",
                }
                color = color_map.get(link["link_type"], "#8E8E93")
                pen = QPen(QColor(color), 2)
                self.scene.addLine(src_pos[0], src_pos[1], dst_pos[0], dst_pos[1], pen)

                # 링크 유형 라벨 + item IDs
                mid_x = (src_pos[0] + dst_pos[0]) / 2
                mid_y = (src_pos[1] + dst_pos[1]) / 2
                src_item = link["source_item_id"] if link["source_item_id"] else ""
                tgt_item = link["target_item_id"] if link["target_item_id"] else ""
                if src_item and tgt_item:
                    label_text = f"{src_item} \u2192 {tgt_item}"
                elif src_item or tgt_item:
                    label_text = f"{link['link_type']} ({src_item or tgt_item})"
                else:
                    label_text = link["link_type"]
                label = self.scene.addText(label_text, QFont("sans-serif", 7))
                label.setDefaultTextColor(QColor(color))
                label.setPos(mid_x - 15, mid_y - 10)

        conn.close()
        self.view.fitInView(self.scene.sceneRect().adjusted(-20, -20, 20, 20), Qt.KeepAspectRatio)

    def _get_item_count(self, doc):
        """Get item count from document's JSON content."""
        try:
            content = doc["content"] if doc["content"] else ""
            if content:
                items = json.loads(content)
                if isinstance(items, list):
                    return len(items)
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
        return 0

    def _draw_doc_card(self, x, y, w, h, name, status, is_linked, doc_id=None, side="left", item_count=0):
        """문서 카드 그리기 - 드래그 가능한 DraggableDocCard 사용"""
        color = STATUS_COLORS.get(status, "#8E8E93")
        border_color = color if is_linked else "#FF3B30"
        border_width = 1.5 if is_linked else 2.5

        pen = QPen(QColor(border_color), border_width)
        brush = QBrush(QColor("#FFFFFF"))

        if doc_id is not None:
            rect = DraggableDocCard(x, y, w, h, doc_id, side, self)
            rect.setPen(pen)
            rect.setBrush(brush)
            self.scene.addItem(rect)
            self._doc_cards.append(rect)
            self._card_original_pens[id(rect)] = pen
        else:
            rect = self.scene.addRect(QRectF(x, y, w, h), pen, brush)

        display_name = name
        if item_count > 0:
            display_name = f"{name} ({item_count} items)"
        name_text = self.scene.addText(display_name, QFont("sans-serif", 8))
        name_text.setDefaultTextColor(QColor("#1C1C1E"))
        name_text.setPos(x + 8, y + 4)
        name_text.setTextWidth(w - 16)

        status_text = self.scene.addText(status, QFont("sans-serif", 7))
        status_text.setDefaultTextColor(QColor(color))
        status_text.setPos(x + 8, y + h - 18)

        if not is_linked:
            warn = self.scene.addText("\u26A0 No trace", QFont("sans-serif", 7))
            warn.setDefaultTextColor(QColor("#FF3B30"))
            warn.setPos(x + w - 65, y + h - 18)

        return rect

    def _restore_card_pen(self, card):
        """카드의 원래 펜 복원"""
        original = self._card_original_pens.get(id(card))
        if original:
            card.setPen(original)

    def _highlight_drop_targets(self, source_side):
        """드롭 가능한 타겟 카드 하이라이트"""
        for card in self._doc_cards:
            if card.side != source_side:
                card.setPen(QPen(QColor("#34C759"), 3))

    def _reset_highlights(self):
        """모든 카드 하이라이트 해제"""
        for card in self._doc_cards:
            self._restore_card_pen(card)

    def _find_card_at(self, scene_pos):
        """씬 좌표에서 DraggableDocCard 찾기"""
        items = self.scene.items(scene_pos)
        for item in items:
            if isinstance(item, DraggableDocCard):
                return item
        return None

    def _create_drag_link(self, source_doc_id, target_doc_id):
        """드래그 앤 드롭으로 추적성 링크 생성"""
        conn = get_connection()
        try:
            TraceabilityModel.create(
                source_doc_id, target_doc_id,
                link_type=LinkType.DERIVES,
                conn=conn
            )
        finally:
            conn.close()
        # Refresh the view
        self._load_data()

    def _add_link(self):
        """추적성 링크 추가 다이얼로그"""
        from PyQt5.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        conn = get_connection()

        docs_1 = DocumentModel.get_by_stage(self.stage_id_1, conn)
        docs_2 = DocumentModel.get_by_stage(self.stage_id_2, conn)

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Traceability Link / 추적성 링크 추가")
        form = QFormLayout(dialog)

        source_combo = QComboBox()
        for d in docs_1:
            source_combo.addItem(d["name"], d["id"])
        form.addRow("Source / 출처:", source_combo)

        target_combo = QComboBox()
        for d in docs_2:
            target_combo.addItem(d["name"], d["id"])
        form.addRow("Target / 대상:", target_combo)

        type_combo = QComboBox()
        type_combo.addItems(LinkType.ALL)
        form.addRow("Type / 유형:", type_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec_():
            TraceabilityModel.create(
                source_combo.currentData(),
                target_combo.currentData(),
                type_combo.currentText(),
                conn=conn
            )
            self._load_data()

        conn.close()
