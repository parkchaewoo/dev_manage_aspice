"""V-Model 다이어그램의 클릭 가능한 노드"""
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QBrush, QPen, QFont, QPainterPath


class ClickableNode(QGraphicsRectItem):
    """SWE 단계를 나타내는 둥근 사각형 노드"""

    def __init__(self, swe_level, name, status, doc_count=0,
                 completion_pct=0, x=0, y=0, width=200, height=80,
                 callback=None, stage_id=None):
        super().__init__(0, 0, width, height)
        self.swe_level = swe_level
        self.stage_id = stage_id
        self.callback = callback
        self.status = status
        self.doc_count = doc_count
        self.completion_pct = completion_pct
        self.setPos(x, y)

        # 상태별 색상
        self.colors = {
            "Not Started": ("#8E8E93", "#F2F2F7"),
            "In Progress": ("#007AFF", "#E8F0FE"),
            "In Review": ("#FF9500", "#FFF3E0"),
            "Completed": ("#34C759", "#E8F5E9"),
        }

        accent, bg = self.colors.get(status, ("#8E8E93", "#F2F2F7"))

        self.setBrush(QBrush(QColor(bg)))
        self.setPen(QPen(QColor(accent), 2))
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setCursor(Qt.PointingHandCursor)
        self.setAcceptHoverEvents(True)

        # 텍스트: SWE 레벨
        self.level_text = QGraphicsTextItem(swe_level, self)
        level_font = QFont("sans-serif", 12, QFont.Bold)
        self.level_text.setFont(level_font)
        self.level_text.setDefaultTextColor(QColor(accent))
        self.level_text.setPos(12, 8)

        # 텍스트: 이름
        self.name_text = QGraphicsTextItem(name, self)
        name_font = QFont("sans-serif", 9)
        self.name_text.setFont(name_font)
        self.name_text.setDefaultTextColor(QColor("#3A3A3C"))
        self.name_text.setPos(12, 30)

        # 텍스트: 문서 수 + 완료율
        info = f"Docs: {doc_count}  |  {completion_pct:.0f}%"
        self.info_text = QGraphicsTextItem(info, self)
        info_font = QFont("sans-serif", 8)
        self.info_text.setFont(info_font)
        self.info_text.setDefaultTextColor(QColor("#8E8E93"))
        self.info_text.setPos(12, 52)

        # 진행바 (하단)
        self._progress_width = int(width * completion_pct / 100) if completion_pct > 0 else 0
        self._accent_color = accent

    def paint(self, painter, option, widget=None):
        """둥근 사각형으로 그리기"""
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 12, 12)
        painter.setClipPath(path)

        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawRoundedRect(self.rect(), 12, 12)

        # 하단 진행바
        if self._progress_width > 0:
            bar_height = 4
            bar_y = self.rect().height() - bar_height
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(self._accent_color)))
            painter.drawRect(QRectF(0, bar_y, self._progress_width, bar_height))

    def hoverEnterEvent(self, event):
        self.setOpacity(0.85)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setOpacity(1.0)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if self.callback and self.stage_id:
            self.callback(self.stage_id)
        super().mousePressEvent(event)
