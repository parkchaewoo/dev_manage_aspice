"""추적성 연결선 - 두께/색상으로 추적 양을 표현"""
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor, QFont


class TraceLine(QGraphicsLineItem):
    """두 단계 사이의 추적성을 나타내는 연결선"""

    def __init__(self, x1, y1, x2, y2, link_count=0, completeness_pct=0,
                 label="", callback=None, stage_ids=None):
        super().__init__(x1, y1, x2, y2)
        self.link_count = link_count
        self.completeness_pct = completeness_pct
        self.callback = callback
        self.stage_ids = stage_ids or ()
        self.setCursor(Qt.PointingHandCursor)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        # 두께: 링크 수에 비례 (최소 1, 최대 8)
        thickness = max(1.5, min(8, link_count * 1.5))

        # 색상: 완성도에 따라
        if completeness_pct >= 100:
            color = "#34C759"  # 초록
        elif completeness_pct >= 50:
            color = "#FF9500"  # 주황
        elif completeness_pct > 0:
            color = "#FFCC00"  # 노랑
        else:
            color = "#FF3B30"  # 빨강

        self.line_color = color
        pen = QPen(QColor(color), thickness, Qt.DashLine)
        pen.setDashPattern([6, 4])
        self.setPen(pen)

        # 라인 중간에 링크 수 표시
        if link_count > 0:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            self.count_text = QGraphicsTextItem(f"{link_count}", self)
            count_font = QFont("sans-serif", 9, QFont.Bold)
            self.count_text.setFont(count_font)
            self.count_text.setDefaultTextColor(QColor(color))
            self.count_text.setPos(mid_x - 8, mid_y - 14)

            # 완성도 퍼센트
            pct_text = QGraphicsTextItem(f"{completeness_pct:.0f}%", self)
            pct_font = QFont("sans-serif", 7)
            pct_text.setFont(pct_font)
            pct_text.setDefaultTextColor(QColor("#8E8E93"))
            pct_text.setPos(mid_x - 12, mid_y + 2)

    def hoverEnterEvent(self, event):
        pen = self.pen()
        pen.setWidth(int(pen.widthF() + 2))
        self.setPen(pen)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        pen = self.pen()
        pen.setWidth(max(1, int(pen.widthF() - 2)))
        self.setPen(pen)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if self.callback and self.stage_ids:
            self.callback(*self.stage_ids)
        super().mousePressEvent(event)
