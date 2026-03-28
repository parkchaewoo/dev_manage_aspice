"""대시보드 차트 위젯 - QPainter 기반"""
import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QFontMetrics


class PieChartWidget(QWidget):
    """원형 차트 (Pie Chart) - QPainter 기반"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.data = []  # list of (label, value, color)
        self.setMinimumSize(250, 250)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_data(self, data):
        """데이터 설정: list of (label, value, color_hex)"""
        self.data = data
        self.update()

    def paintEvent(self, event):
        if not self.data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Title
        title_h = 0
        if self.title:
            painter.setPen(QColor("#1C1C1E"))
            title_font = QFont("sans-serif", 12, QFont.Bold)
            painter.setFont(title_font)
            painter.drawText(QRectF(0, 8, w, 24), Qt.AlignCenter, self.title)
            title_h = 32

        # Chart area
        legend_h = len(self.data) * 20 + 10
        chart_area_h = h - title_h - legend_h
        diameter = min(w - 40, chart_area_h - 20)
        if diameter < 60:
            diameter = 60
        cx = w / 2
        cy = title_h + chart_area_h / 2
        rect = QRectF(cx - diameter / 2, cy - diameter / 2, diameter, diameter)

        total = sum(v for _, v, _ in self.data)
        if total == 0:
            painter.setPen(QColor("#C7C7CC"))
            painter.setFont(QFont("sans-serif", 10))
            painter.drawText(QRectF(0, title_h, w, chart_area_h), Qt.AlignCenter, "No data")
            return

        start_angle = 90 * 16  # start from top
        for label, value, color in self.data:
            if value == 0:
                continue
            span = int(value / total * 360 * 16)
            painter.setPen(QPen(QColor("#FFFFFF"), 2))
            painter.setBrush(QBrush(QColor(color)))
            painter.drawPie(rect, start_angle, span)
            start_angle += span

        # Legend
        legend_y = h - legend_h + 5
        legend_font = QFont("sans-serif", 9)
        painter.setFont(legend_font)
        fm = QFontMetrics(legend_font)

        for i, (label, value, color) in enumerate(self.data):
            y = legend_y + i * 20
            # Color swatch
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(16, y + 2, 12, 12), 2, 2)
            # Text
            painter.setPen(QColor("#3A3A3C"))
            pct = (value / total * 100) if total > 0 else 0
            text = f"{label}: {value} ({pct:.0f}%)"
            painter.drawText(QRectF(34, y, w - 50, 18), Qt.AlignVCenter, text)

        painter.end()


class BarChartWidget(QWidget):
    """수평 막대 차트 (Horizontal Bar Chart)"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.data = []  # list of (label, value, max_value, color)
        self.setMinimumSize(250, 150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_data(self, data):
        """데이터 설정: list of (label, value, max_value, color_hex)"""
        self.data = data
        min_h = 40 + len(data) * 36 + 10
        self.setMinimumHeight(max(150, min_h))
        self.update()

    def paintEvent(self, event):
        if not self.data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Title
        title_h = 0
        if self.title:
            painter.setPen(QColor("#1C1C1E"))
            title_font = QFont("sans-serif", 12, QFont.Bold)
            painter.setFont(title_font)
            painter.drawText(QRectF(0, 8, w, 24), Qt.AlignCenter, self.title)
            title_h = 36

        # Bars
        label_font = QFont("sans-serif", 9)
        painter.setFont(label_font)
        fm = QFontMetrics(label_font)

        label_w = 0
        for label, _, _, _ in self.data:
            lw = fm.horizontalAdvance(label)
            if lw > label_w:
                label_w = lw
        label_w += 16

        bar_x = label_w + 8
        bar_max_w = w - bar_x - 60
        bar_h = 18
        gap = 36

        for i, (label, value, max_value, color) in enumerate(self.data):
            y = title_h + i * gap + 4

            # Label
            painter.setPen(QColor("#3A3A3C"))
            painter.setFont(label_font)
            painter.drawText(
                QRectF(8, y, label_w, bar_h + 4),
                Qt.AlignVCenter | Qt.AlignRight, label
            )

            # Background bar
            painter.setBrush(QBrush(QColor("#E5E5EA")))
            painter.setPen(Qt.NoPen)
            bg_rect = QRectF(bar_x, y + 2, bar_max_w, bar_h)
            painter.drawRoundedRect(bg_rect, 4, 4)

            # Value bar
            ratio = (value / max_value) if max_value > 0 else 0
            bar_w = bar_max_w * ratio
            if bar_w > 0:
                painter.setBrush(QBrush(QColor(color)))
                painter.drawRoundedRect(QRectF(bar_x, y + 2, bar_w, bar_h), 4, 4)

            # Percentage text
            painter.setPen(QColor("#3A3A3C"))
            pct_text = f"{ratio * 100:.0f}%"
            painter.drawText(
                QRectF(bar_x + bar_max_w + 6, y, 44, bar_h + 4),
                Qt.AlignVCenter, pct_text
            )

        painter.end()


class GaugeWidget(QWidget):
    """원형 게이지 (Circular Progress Gauge)"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.percentage = 0
        self.label_text = ""
        self.setMinimumSize(180, 180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_value(self, percentage, label=""):
        """퍼센트 및 라벨 설정"""
        self.percentage = max(0, min(100, percentage))
        self.label_text = label
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Title
        title_h = 0
        if self.title:
            painter.setPen(QColor("#1C1C1E"))
            title_font = QFont("sans-serif", 12, QFont.Bold)
            painter.setFont(title_font)
            painter.drawText(QRectF(0, 8, w, 24), Qt.AlignCenter, self.title)
            title_h = 32

        # Gauge area
        avail_h = h - title_h - 30  # leave space for bottom label
        diameter = min(w - 40, avail_h - 10)
        if diameter < 60:
            diameter = 60
        line_w = max(8, diameter // 10)
        cx = w / 2
        cy = title_h + avail_h / 2
        rect = QRectF(cx - diameter / 2, cy - diameter / 2, diameter, diameter)

        # Background arc (full circle)
        pen_bg = QPen(QColor("#E5E5EA"), line_w, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(rect, 0, 360 * 16)

        # Value arc
        if self.percentage <= 30:
            arc_color = "#FF3B30"
        elif self.percentage <= 60:
            arc_color = "#FF9500"
        elif self.percentage <= 85:
            arc_color = "#007AFF"
        else:
            arc_color = "#34C759"

        pen_val = QPen(QColor(arc_color), line_w, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen_val)
        span = int(self.percentage / 100 * 360 * 16)
        painter.drawArc(rect, 90 * 16, -span)

        # Center percentage text
        painter.setPen(QColor("#1C1C1E"))
        pct_font = QFont("sans-serif", max(14, diameter // 5), QFont.Bold)
        painter.setFont(pct_font)
        painter.drawText(rect, Qt.AlignCenter, f"{self.percentage:.0f}%")

        # Bottom label
        if self.label_text:
            painter.setPen(QColor("#8E8E93"))
            painter.setFont(QFont("sans-serif", 9))
            painter.drawText(
                QRectF(0, h - 24, w, 20), Qt.AlignCenter, self.label_text
            )

        painter.end()
