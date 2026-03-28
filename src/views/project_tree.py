"""프로젝트 트리 뷰 - OEM > Project > Phase > SWE Stage 계층"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QPushButton, QHBoxLayout, QMenu, QAction
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSignal

from src.models.database import get_connection
from src.models.oem import OemModel
from src.models.project import ProjectModel
from src.models.phase import PhaseModel
from src.models.stage import StageModel
from src.utils.constants import SWE_STAGES, STATUS_COLORS, StageStatus


class ProjectTreeWidget(QWidget):
    oem_selected = pyqtSignal(int)
    project_selected = pyqtSignal(int)
    phase_selected = pyqtSignal(int)
    stage_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 트리뷰
        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree.clicked.connect(self._on_clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._context_menu)
        layout.addWidget(self.tree)

        # 하단 버튼
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(8, 8, 8, 8)

        self.btn_new_project = QPushButton("+ New Project")
        self.btn_new_project.setProperty("secondary", True)
        self.btn_new_project.clicked.connect(self._new_project)
        btn_layout.addWidget(self.btn_new_project)

        layout.addLayout(btn_layout)

        self.model = QStandardItemModel()
        self.tree.setModel(self.model)

    def refresh(self):
        """트리 데이터 새로고침"""
        self.model.clear()
        conn = get_connection()

        oems = OemModel.get_all(conn)
        for oem in oems:
            oem_item = QStandardItem(f"  {oem['name']}")
            oem_font = QFont()
            oem_font.setBold(True)
            oem_font.setPointSize(13)
            oem_item.setFont(oem_font)
            oem_item.setData(("oem", oem["id"]), Qt.UserRole)
            oem_item.setForeground(QColor("#3A3A3C"))

            projects = ProjectModel.get_by_oem(oem["id"], conn)
            for proj in projects:
                proj_item = QStandardItem(f"  {proj['name']}")
                proj_font = QFont()
                proj_font.setPointSize(12)
                proj_item.setFont(proj_font)
                proj_item.setData(("project", proj["id"]), Qt.UserRole)
                proj_item.setForeground(QColor("#1C1C1E"))

                phases = PhaseModel.get_by_project(proj["id"], conn)
                if phases:
                    # 4-level tree: OEM > Project > Phase > Stage
                    for phase in phases:
                        phase_status = phase["status"]
                        phase_icon = "◆" if phase_status == "Completed" else "◇"
                        phase_item = QStandardItem(
                            f"  {phase_icon} {phase['name']} [{phase_status}]"
                        )
                        phase_font = QFont()
                        phase_font.setPointSize(11)
                        phase_font.setItalic(True)
                        phase_item.setFont(phase_font)
                        phase_item.setData(("phase", phase["id"]), Qt.UserRole)
                        phase_color = "#34C759" if phase_status == "Completed" else "#007AFF"
                        phase_item.setForeground(QColor(phase_color))

                        stages = StageModel.get_by_phase(phase["id"], conn)
                        for stage in stages:
                            stage_item = self._create_stage_item(stage)
                            phase_item.appendRow(stage_item)

                        proj_item.appendRow(phase_item)
                else:
                    # Fallback: stages without phases (legacy)
                    stages = StageModel.get_by_project(proj["id"], conn)
                    for stage in stages:
                        stage_item = self._create_stage_item(stage)
                        proj_item.appendRow(stage_item)

                oem_item.appendRow(proj_item)

            self.model.appendRow(oem_item)

        conn.close()
        self.tree.expandAll()

    def _create_stage_item(self, stage):
        """Create a tree item for a stage."""
        swe = stage["swe_level"]
        status = stage["status"]
        color = STATUS_COLORS.get(status, "#8E8E93")

        # 상태 아이콘
        status_icon = "○"
        if status == StageStatus.COMPLETED:
            status_icon = "●"
        elif status == StageStatus.IN_PROGRESS:
            status_icon = "◐"
        elif status == StageStatus.IN_REVIEW:
            status_icon = "◑"

        stage_name = SWE_STAGES.get(swe, {}).get("name_ko", swe)
        stage_item = QStandardItem(f"  {status_icon} {swe}: {stage_name}")
        stage_item.setData(("stage", stage["id"]), Qt.UserRole)
        stage_item.setForeground(QColor(color))
        return stage_item

    def _on_clicked(self, index):
        item = self.model.itemFromIndex(index)
        if item:
            data = item.data(Qt.UserRole)
            if data:
                item_type, item_id = data
                if item_type == "oem":
                    self.oem_selected.emit(item_id)
                elif item_type == "project":
                    self.project_selected.emit(item_id)
                elif item_type == "phase":
                    self.phase_selected.emit(item_id)
                elif item_type == "stage":
                    self.stage_selected.emit(item_id)

    def _context_menu(self, position):
        index = self.tree.indexAt(position)
        if not index.isValid():
            return
        item = self.model.itemFromIndex(index)
        data = item.data(Qt.UserRole)
        if not data:
            return

        menu = QMenu()
        item_type, item_id = data

        if item_type == "project":
            menu.addAction("Open V-Model", lambda: self.project_selected.emit(item_id))
            menu.addAction("New Phase...", lambda: self._new_phase(item_id))
            menu.addSeparator()
            menu.addAction("Delete Project", lambda: self._delete_project(item_id))
        elif item_type == "phase":
            menu.addAction("View Phase", lambda: self.phase_selected.emit(item_id))
            menu.addAction("Complete & Advance to Next Phase / 완료 후 다음 단계로",
                          lambda: self._complete_and_advance(item_id))
            menu.addSeparator()
            menu.addAction("New Phase (Empty)...", lambda: self._new_phase_for_phase(item_id))
            menu.addAction("Inherit from This Phase...", lambda: self._inherit_phase(item_id))
            menu.addSeparator()
            menu.addAction("Delete Phase", lambda: self._delete_phase(item_id))
        elif item_type == "stage":
            menu.addAction("View Details", lambda: self.stage_selected.emit(item_id))

        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def _new_project(self):
        from src.views.new_project_dialog import NewProjectDialog
        dialog = NewProjectDialog(self.window())
        if dialog.exec_():
            self.refresh()

    def _new_phase(self, project_id):
        """Open new phase dialog for a project."""
        from src.views.new_phase_dialog import NewPhaseDialog
        dialog = NewPhaseDialog(project_id, parent=self.window())
        if dialog.exec_():
            self.refresh()

    def _new_phase_for_phase(self, phase_id):
        """Create a new empty phase in the same project as this phase."""
        from src.models.phase import PhaseModel
        phase = PhaseModel.get_by_id(phase_id)
        if phase:
            self._new_phase(phase["project_id"])

    def _inherit_phase(self, source_phase_id):
        """Create a new phase inherited from the given phase."""
        from src.views.new_phase_dialog import NewPhaseDialog
        from src.models.phase import PhaseModel
        phase = PhaseModel.get_by_id(source_phase_id)
        if phase:
            dialog = NewPhaseDialog(
                phase["project_id"],
                inherit_from_phase_id=source_phase_id,
                parent=self.window()
            )
            if dialog.exec_():
                self.refresh()

    def _complete_and_advance(self, phase_id):
        """현재 Phase를 완료하고 다음 Phase를 상속하여 생성"""
        from PyQt5.QtWidgets import QMessageBox
        from src.models.phase import PhaseModel
        from src.models.oem import OemModel
        from src.models.project import ProjectModel
        from src.utils.yaml_helpers import load_yaml_string

        phase = PhaseModel.get_by_id(phase_id)
        if not phase:
            return

        project = ProjectModel.get_by_id(phase["project_id"])
        oem = OemModel.get_by_id(project["oem_id"]) if project else None

        # OEM config에서 Phase 목록 가져오기
        oem_phases = []
        if oem and oem["config_yaml"]:
            try:
                config = load_yaml_string(oem["config_yaml"])
                oem_phases = config.get("phases", []) if config else []
            except Exception:
                pass

        # 현재 Phase 다음 단계 결정
        current_name = phase["name"]
        next_name = None
        if oem_phases and current_name in oem_phases:
            idx = oem_phases.index(current_name)
            if idx + 1 < len(oem_phases):
                next_name = oem_phases[idx + 1]

        if not next_name:
            next_name = f"{current_name} + 1"

        reply = QMessageBox.question(
            self, "Complete & Advance / 완료 및 다음 단계",
            f"Current phase '{current_name}' will be marked as Completed.\n"
            f"Next phase '{next_name}' will be created inheriting approved documents.\n\n"
            f"현재 단계 '{current_name}'을(를) 완료로 표시하고\n"
            f"다음 단계 '{next_name}'을(를) 생성합니다.\n"
            f"승인된 문서가 자동으로 상속됩니다.\n\n"
            f"Proceed / 진행하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        conn = get_connection()
        try:
            # 1. 현재 Phase를 Completed로 변경
            PhaseModel.update(phase_id, status="Completed", conn=conn)

            # 2. 다음 Phase 상속 생성
            from src.services.phase_service import create_phase_inherited
            new_phase_id = create_phase_inherited(
                phase["project_id"], next_name, phase_id,
                description=f"Inherited from {current_name}",
                conn=conn
            )

            conn.close()
            QMessageBox.information(
                self, "Success / 성공",
                f"Phase '{current_name}' completed.\n"
                f"Phase '{next_name}' created with inherited documents.\n\n"
                f"'{current_name}' 완료, '{next_name}' 생성 완료."
            )
            self.refresh()
        except Exception as e:
            conn.close()
            QMessageBox.warning(self, "Error", f"Failed: {e}")

    def _delete_phase(self, phase_id):
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Delete Phase / 개발 단계 삭제",
            "Are you sure you want to delete this phase?\n"
            "All stages, documents, and checklists in this phase will be deleted.\n"
            "이 개발 단계를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            PhaseModel.delete(phase_id)
            try:
                self.window().refresh_all()
            except Exception:
                self.refresh()

    def _delete_project(self, project_id):
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Delete Project / 프로젝트 삭제",
            "Are you sure you want to delete this project?\n이 프로젝트를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ProjectModel.delete(project_id)
            try:
                self.window().refresh_all()
            except Exception:
                self.refresh()
