"""일정 관리 / 간트 스타일 뷰"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QScrollArea, QDateEdit, QLineEdit, QComboBox, QDialog, QFormLayout
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QBrush, QPainter, QPen

from src.models.database import get_connection
from src.models.schedule import ScheduleModel
from src.models.stage import StageModel
from src.models.project import ProjectModel
from src.utils.constants import SWE_STAGES, MilestoneStatus, STATUS_COLORS


class ScheduleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_id = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 헤더
        header = QHBoxLayout()
        self.title_label = QLabel("Schedule / 일정 관리")
        self.title_label.setProperty("heading", True)
        header.addWidget(self.title_label)
        header.addStretch()

        self.btn_add = QPushButton("+ Add Milestone / 마일스톤 추가")
        self.btn_add.clicked.connect(self._add_milestone)
        header.addWidget(self.btn_add)
        layout.addLayout(header)

        # 단계별 일정 요약
        self.stage_frame = QFrame()
        self.stage_frame.setProperty("card", True)
        self.stage_layout = QVBoxLayout(self.stage_frame)
        self.stage_layout.addWidget(QLabel("Stage Schedule / 단계별 일정"))

        self.stage_table = QTableWidget()
        self.stage_table.setColumnCount(5)
        self.stage_table.setHorizontalHeaderLabels([
            "Stage / 단계", "Status / 상태",
            "Planned Start", "Planned End", "Progress"
        ])
        self.stage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stage_table.verticalHeader().setVisible(False)
        self.stage_layout.addWidget(self.stage_table)
        layout.addWidget(self.stage_frame)

        # 마일스톤 테이블
        milestone_frame = QFrame()
        milestone_frame.setProperty("card", True)
        milestone_layout = QVBoxLayout(milestone_frame)
        milestone_layout.addWidget(QLabel("Milestones / 마일스톤"))

        self.milestone_table = QTableWidget()
        self.milestone_table.setColumnCount(5)
        self.milestone_table.setHorizontalHeaderLabels([
            "Milestone / 마일스톤", "Stage / 단계",
            "Due Date / 마감일", "Status / 상태", "Actions"
        ])
        self.milestone_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.milestone_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.milestone_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.milestone_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.milestone_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.milestone_table.verticalHeader().setVisible(False)
        milestone_layout.addWidget(self.milestone_table)
        layout.addWidget(milestone_frame)

    def load_project(self, project_id):
        """프로젝트 일정 로드"""
        self.project_id = project_id
        conn = get_connection()

        project = ProjectModel.get_by_id(project_id, conn)
        if project:
            self.title_label.setText(f"Schedule: {project['name']} / 일정 관리")

        # 단계 일정
        stages = StageModel.get_by_project(project_id, conn)
        self.stage_table.setRowCount(len(stages))

        for i, stage in enumerate(stages):
            swe = stage["swe_level"]
            name = SWE_STAGES.get(swe, {}).get("name_ko", swe)
            self.stage_table.setItem(i, 0, QTableWidgetItem(f"{swe}: {name}"))

            status_item = QTableWidgetItem(stage["status"])
            color = STATUS_COLORS.get(stage["status"], "#8E8E93")
            status_item.setForeground(QColor(color))
            self.stage_table.setItem(i, 1, status_item)

            self.stage_table.setItem(i, 2, QTableWidgetItem(stage["planned_start"] or "-"))
            self.stage_table.setItem(i, 3, QTableWidgetItem(stage["planned_end"] or "-"))

            stats = StageModel.get_completion_stats(stage["id"], conn)
            pct_item = QTableWidgetItem(f"{stats['overall_pct']:.0f}%")
            self.stage_table.setItem(i, 4, pct_item)

        # 마일스톤
        milestones = ScheduleModel.get_by_project(project_id, conn)
        self.milestone_table.setRowCount(len(milestones))

        for i, ms in enumerate(milestones):
            self.milestone_table.setItem(i, 0, QTableWidgetItem(ms["name"]))
            self.milestone_table.setItem(i, 1, QTableWidgetItem(ms["swe_level"] or "-"))
            self.milestone_table.setItem(i, 2, QTableWidgetItem(ms["due_date"] or "-"))

            status_item = QTableWidgetItem(ms["status"])
            color = STATUS_COLORS.get(ms["status"], "#8E8E93")
            status_item.setForeground(QColor(color))
            self.milestone_table.setItem(i, 3, status_item)

            # 완료 버튼
            btn = QPushButton("Complete" if ms["status"] != "Completed" else "Done")
            btn.setMaximumWidth(80)
            btn.setEnabled(ms["status"] != "Completed")
            btn.setProperty("secondary", True)
            btn.clicked.connect(lambda _, mid=ms["id"]: self._complete_milestone(mid))
            self.milestone_table.setCellWidget(i, 4, btn)

        conn.close()

    def _add_milestone(self):
        if not self.project_id:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Milestone / 마일스톤 추가")
        dialog.setMinimumWidth(400)
        form = QFormLayout(dialog)

        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Milestone name / 마일스톤 이름")
        form.addRow("Name / 이름:", name_edit)

        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate().addDays(30))
        date_edit.setCalendarPopup(True)
        form.addRow("Due Date / 마감일:", date_edit)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save / 저장")
        save_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("Cancel / 취소")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        form.addRow(btn_layout)

        if dialog.exec_():
            ScheduleModel.create(
                self.project_id,
                name_edit.text(),
                date_edit.date().toString("yyyy-MM-dd")
            )
            self.load_project(self.project_id)

    def _complete_milestone(self, milestone_id):
        from datetime import date
        ScheduleModel.update(
            milestone_id,
            status="Completed",
            completed_date=date.today().isoformat()
        )
        self.load_project(self.project_id)
