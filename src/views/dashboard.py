"""프로젝트 대시보드 - 개요 화면"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QProgressBar, QScrollArea, QPushButton,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from src.models.database import get_connection
from src.models.project import ProjectModel
from src.models.stage import StageModel
from src.models.oem import OemModel
from src.utils.constants import SWE_STAGES, STATUS_COLORS, StageStatus
from src.widgets.chart_widgets import PieChartWidget, BarChartWidget, GaugeWidget
from src.widgets.notification_banner import NotificationBanner


class DashboardWidget(QWidget):
    project_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_widget = QWidget()
        self.content_layout = QVBoxLayout(scroll_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # Notification banners (Feature 10)
        self.overdue_banner = NotificationBanner(NotificationBanner.TYPE_OVERDUE)
        self.overdue_banner.hide()
        self.content_layout.addWidget(self.overdue_banner)

        self.upcoming_banner = NotificationBanner(NotificationBanner.TYPE_UPCOMING)
        self.upcoming_banner.hide()
        self.content_layout.addWidget(self.upcoming_banner)

        # 타이틀
        self.title_label = QLabel("Dashboard / 대시보드")
        self.title_label.setProperty("heading", True)
        self.content_layout.addWidget(self.title_label)

        # 프로젝트 카드 영역
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(16)
        self.content_layout.addLayout(self.cards_layout)

        # 선택된 프로젝트 상세
        self.detail_frame = QFrame()
        self.detail_frame.setProperty("card", True)
        self.detail_layout = QVBoxLayout(self.detail_frame)
        self.detail_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.addWidget(self.detail_frame)
        self.detail_frame.hide()

        self.content_layout.addStretch()

    def refresh(self):
        """전체 프로젝트 목록으로 대시보드 새로고침"""
        self._clear_cards()
        conn = get_connection()
        projects = ProjectModel.get_all(conn)

        self.title_label.setText(f"Dashboard / 대시보드  ({len(projects)} projects)")

        for i, proj in enumerate(projects):
            card = self._create_project_card(proj, conn)
            row, col = divmod(i, 3)
            self.cards_layout.addWidget(card, row, col)

        conn.close()

    def load_project(self, project_id):
        """특정 프로젝트 상세 로드"""
        conn = get_connection()
        project = ProjectModel.get_by_id(project_id, conn)
        if not project:
            conn.close()
            return

        oem = OemModel.get_by_id(project["oem_id"], conn)
        stages = StageModel.get_by_project(project_id, conn)

        # 상세 프레임 업데이트
        self._clear_layout(self.detail_layout)

        # 프로젝트 제목 + Export 버튼
        title_row = QHBoxLayout()
        title = QLabel(f"{oem['name']} > {project['name']}")
        title.setProperty("heading", True)
        title_row.addWidget(title)
        title_row.addStretch()

        export_btn = QPushButton("Export Report")
        export_btn.setProperty("secondary", True)
        export_btn.setMaximumWidth(140)
        export_btn.clicked.connect(lambda: self._export_report(project_id))
        title_row.addWidget(export_btn)
        self.detail_layout.addLayout(title_row)

        status_label = QLabel(f"Status: {project['status']}")
        status_label.setProperty("subheading", True)
        self.detail_layout.addWidget(status_label)

        # 단계별 진행 상황
        stages_frame = QFrame()
        stages_layout = QVBoxLayout(stages_frame)
        stages_layout.setSpacing(12)

        subtitle = QLabel("Stage Progress / 단계별 진행 상황")
        subtitle.setProperty("subheading", True)
        stages_layout.addWidget(subtitle)

        for stage in stages:
            swe = stage["swe_level"]
            status = stage["status"]
            stats = StageModel.get_completion_stats(stage["id"], conn)

            row_layout = QHBoxLayout()

            name_label = QLabel(f"{swe}: {SWE_STAGES[swe]['name_ko']}")
            name_label.setMinimumWidth(250)
            row_layout.addWidget(name_label)

            # 상태 배지
            badge = QLabel(f" {status} ")
            color = STATUS_COLORS.get(status, "#8E8E93")
            badge.setStyleSheet(
                f"background-color: {color}; color: white; "
                f"border-radius: 8px; padding: 4px 10px; font-size: 12px;"
            )
            row_layout.addWidget(badge)

            # 진행바
            pbar = QProgressBar()
            pbar.setValue(int(stats["overall_pct"]))
            pbar.setMaximumHeight(8)
            pbar.setTextVisible(False)
            row_layout.addWidget(pbar, 1)

            pct_label = QLabel(f"{stats['overall_pct']:.0f}%")
            pct_label.setProperty("caption", True)
            pct_label.setMinimumWidth(40)
            pct_label.setAlignment(Qt.AlignRight)
            row_layout.addWidget(pct_label)

            stages_layout.addLayout(row_layout)

        self.detail_layout.addWidget(stages_frame)

        # === Charts Section (Feature 9) ===
        charts_title = QLabel("Analytics / 분석")
        charts_title.setProperty("subheading", True)
        self.detail_layout.addWidget(charts_title)

        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        # Collect stage status counts for PieChart
        status_counts = {}
        stage_stats_list = []
        total_pct_sum = 0
        for stage in stages:
            status = stage["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
            stats = StageModel.get_completion_stats(stage["id"], conn)
            stage_stats_list.append((stage["swe_level"], stats["overall_pct"]))
            total_pct_sum += stats["overall_pct"]

        # PieChartWidget - stage status distribution
        pie_frame = QFrame()
        pie_frame.setProperty("card", True)
        pie_layout = QVBoxLayout(pie_frame)
        pie_layout.setContentsMargins(12, 12, 12, 12)
        pie_chart = PieChartWidget("Stage Status Distribution")
        pie_data = []
        status_order = [
            (StageStatus.NOT_STARTED, "#8E8E93"),
            (StageStatus.IN_PROGRESS, "#007AFF"),
            (StageStatus.IN_REVIEW, "#FF9500"),
            (StageStatus.COMPLETED, "#34C759"),
        ]
        for s_name, s_color in status_order:
            count = status_counts.get(s_name, 0)
            if count > 0:
                pie_data.append((s_name, count, s_color))
        pie_chart.set_data(pie_data)
        pie_layout.addWidget(pie_chart)
        charts_row.addWidget(pie_frame)

        # BarChartWidget - per-stage document completion
        bar_frame = QFrame()
        bar_frame.setProperty("card", True)
        bar_layout = QVBoxLayout(bar_frame)
        bar_layout.setContentsMargins(12, 12, 12, 12)
        bar_chart = BarChartWidget("Document Completion by Stage")
        bar_data = []
        for swe_level, pct in stage_stats_list:
            color = "#34C759" if pct >= 80 else ("#FF9500" if pct >= 40 else "#007AFF")
            bar_data.append((swe_level, pct, 100, color))
        bar_chart.set_data(bar_data)
        bar_layout.addWidget(bar_chart)
        charts_row.addWidget(bar_frame)

        # GaugeWidget - overall project progress
        gauge_frame = QFrame()
        gauge_frame.setProperty("card", True)
        gauge_layout = QVBoxLayout(gauge_frame)
        gauge_layout.setContentsMargins(12, 12, 12, 12)
        gauge = GaugeWidget("Overall Progress")
        overall_pct = total_pct_sum / len(stages) if stages else 0
        gauge.set_value(overall_pct, "Project Completion")
        gauge_layout.addWidget(gauge)
        charts_row.addWidget(gauge_frame)

        self.detail_layout.addLayout(charts_row)

        self.detail_frame.show()
        conn.close()

    def _create_project_card(self, project, conn):
        """프로젝트 요약 카드 생성"""
        card = QFrame()
        card.setProperty("card", True)
        card.setMinimumSize(300, 180)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet("""
            QFrame[card="true"] { background-color: #FFFFFF; border-radius: 12px; }
            QFrame[card="true"]:hover { background-color: #F8F8FA; }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # OEM 이름
        oem_label = QLabel(project["oem_name"])
        oem_label.setProperty("caption", True)
        layout.addWidget(oem_label)

        # 프로젝트 이름
        name_label = QLabel(project["name"])
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        name_label.setFont(name_font)
        layout.addWidget(name_label)

        # 상태
        status_label = QLabel(project["status"])
        color = "#34C759" if project["status"] == "Completed" else "#007AFF"
        status_label.setStyleSheet(f"color: {color}; font-weight: 600;")
        layout.addWidget(status_label)

        # 단계 진행 요약
        stages = StageModel.get_by_project(project["id"], conn)
        completed = sum(1 for s in stages if s["status"] == StageStatus.COMPLETED)
        total = len(stages)
        progress_label = QLabel(f"Stages: {completed}/{total} completed")
        progress_label.setProperty("caption", True)
        layout.addWidget(progress_label)

        pbar = QProgressBar()
        pbar.setValue(int(completed / total * 100) if total > 0 else 0)
        pbar.setMaximumHeight(6)
        pbar.setTextVisible(False)
        layout.addWidget(pbar)

        layout.addStretch()

        # 클릭 이벤트
        card.mousePressEvent = lambda e, pid=project["id"]: self.project_selected.emit(pid)

        return card

    def _export_report(self, project_id):
        """Export full project report as Markdown."""
        from src.services.export_service import export_project_report
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Project Report", "", "Markdown Files (*.md);;All Files (*)"
        )
        if path:
            try:
                export_project_report(project_id, path)
                QMessageBox.information(self, "Export", f"Report exported to:\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))

    def update_notifications(self, overdue_items, upcoming_items):
        """알림 배너 업데이트 (Feature 10)"""
        self.overdue_banner.set_notifications(overdue_items)
        self.upcoming_banner.set_notifications(upcoming_items)

    def _clear_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
