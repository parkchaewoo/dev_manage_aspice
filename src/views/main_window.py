"""메인 윈도우 - iOS 캘린더 스타일"""
from PyQt5.QtWidgets import (
    QMainWindow, QDockWidget, QStackedWidget, QToolBar,
    QAction, QMessageBox, QWidget, QVBoxLayout, QLabel, QStatusBar,
    QApplication, QLineEdit, QFileDialog
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QIcon

from src.models.database import get_connection
from src.views.project_tree import ProjectTreeWidget
from src.views.dashboard import DashboardWidget
from src.views.stage_detail import StageDetailWidget
from src.views.vmodel_view import VModelWidget
from src.views.traceability_matrix import TraceabilityMatrixWidget
from src.views.schedule_view import ScheduleWidget
from src.views.oem_config_dialog import OemConfigDialog
from src.views.guide_panel import GuidePanel
from src.views.search_widget import SearchWidget
from src.utils.styles import get_stylesheet, get_saved_theme, save_theme
from src.services.notification_service import get_notification_summary


class MainWindow(QMainWindow):
    def __init__(self, version="0.1.0", parent=None):
        super().__init__(parent)
        self.version = version
        self.current_project_id = None
        self.current_phase_id = None
        self.current_stage_id = None
        self.current_theme = get_saved_theme()
        self.setWindowTitle(f"ASPICE Process Manager v{version}")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        self._setup_central()
        self._setup_dock()
        self._setup_toolbar()
        self._setup_menubar()
        self._setup_statusbar()

        # Apply saved theme
        QApplication.instance().setStyleSheet(get_stylesheet(self.current_theme))

        # 초기 화면은 대시보드
        self._show_dashboard()

        # Check notifications on startup
        self._check_notifications()

    def _setup_central(self):
        """중앙 스택 위젯 설정"""
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 각 뷰 생성
        self.dashboard = DashboardWidget()
        self.stage_detail = StageDetailWidget()
        self.vmodel_view = VModelWidget()
        self.trace_matrix = TraceabilityMatrixWidget()
        self.schedule_view = ScheduleWidget()
        self.guide_panel = GuidePanel()

        # 스택에 추가
        self.stack.addWidget(self.dashboard)      # 0
        self.stack.addWidget(self.stage_detail)    # 1
        self.stack.addWidget(self.vmodel_view)     # 2
        self.stack.addWidget(self.trace_matrix)    # 3
        self.stack.addWidget(self.schedule_view)   # 4

        # 시그널 연결
        self.dashboard.project_selected.connect(self._on_project_selected)
        self.stage_detail.back_requested.connect(self._show_dashboard)
        self.vmodel_view.stage_clicked.connect(self._on_stage_clicked)

    def _setup_dock(self):
        """좌측 프로젝트 트리 독 위젯"""
        self.tree_dock = QDockWidget("Projects", self)
        self.tree_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.tree_dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.tree_dock.setMinimumWidth(280)

        self.project_tree = ProjectTreeWidget()
        self.tree_dock.setWidget(self.project_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tree_dock)

        # 트리 선택 시그널
        self.project_tree.oem_selected.connect(self._on_oem_selected)
        self.project_tree.project_selected.connect(self._on_project_selected)
        self.project_tree.phase_selected.connect(self._on_phase_selected)
        self.project_tree.stage_selected.connect(self._on_stage_clicked)

        # 가이드 패널 독
        self.guide_dock = QDockWidget("Guide / 가이드", self)
        self.guide_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        self.guide_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.guide_dock.setWidget(self.guide_panel)
        self.guide_dock.setMinimumWidth(300)
        self.addDockWidget(Qt.RightDockWidgetArea, self.guide_dock)

    def _setup_toolbar(self):
        """툴바 설정"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.act_dashboard = QAction("Dashboard", self)
        self.act_dashboard.triggered.connect(self._show_dashboard)
        toolbar.addAction(self.act_dashboard)

        self.act_vmodel = QAction("V-Model", self)
        self.act_vmodel.triggered.connect(self._show_vmodel)
        toolbar.addAction(self.act_vmodel)

        self.act_schedule = QAction("Schedule", self)
        self.act_schedule.triggered.connect(self._show_schedule)
        toolbar.addAction(self.act_schedule)

        self.act_matrix = QAction("Traceability", self)
        self.act_matrix.triggered.connect(self._show_trace_matrix)
        toolbar.addAction(self.act_matrix)

        self.act_report = QAction("Generate ASPICE Report", self)
        self.act_report.triggered.connect(self._generate_aspice_report)
        toolbar.addAction(self.act_report)

        # Search input in toolbar
        toolbar.addSeparator()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search / 검색...")
        self.search_input.setMaximumWidth(220)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(self._open_search)
        toolbar.addWidget(self.search_input)

        # Search popup widget
        self.search_widget = SearchWidget(self)
        self.search_widget.result_selected.connect(self._on_search_result)

    def _setup_menubar(self):
        """메뉴바 설정"""
        menubar = self.menuBar()

        # File 메뉴
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Refresh", self.refresh_all)
        file_menu.addSeparator()
        file_menu.addAction("Backup Database...", self._backup_database)
        file_menu.addAction("Restore Database...", self._restore_database)
        file_menu.addSeparator()
        file_menu.addAction("Export as JSON...", self._export_json)
        file_menu.addAction("Import from JSON...", self._import_json)
        file_menu.addSeparator()
        file_menu.addAction("Reset Demo Data / 데모 초기화...", self._reset_demo_data)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Project 메뉴
        project_menu = menubar.addMenu("Project")
        project_menu.addAction("New Project...", self._new_project)
        project_menu.addAction("New Phase...", self._new_phase)

        # OEM 메뉴
        oem_menu = menubar.addMenu("OEM")
        oem_menu.addAction("Manage OEMs...", self._manage_oems)

        # View 메뉴
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Dashboard", self._show_dashboard)
        view_menu.addAction("V-Model", self._show_vmodel)
        view_menu.addAction("Schedule", self._show_schedule)
        view_menu.addAction("Traceability Matrix", self._show_trace_matrix)
        view_menu.addSeparator()
        view_menu.addAction(self.tree_dock.toggleViewAction())
        view_menu.addAction(self.guide_dock.toggleViewAction())
        view_menu.addSeparator()
        self.act_toggle_theme = QAction("Toggle Dark Mode", self)
        self.act_toggle_theme.triggered.connect(self._toggle_theme)
        view_menu.addAction(self.act_toggle_theme)

        # Help 메뉴
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self._show_about)

    def _setup_statusbar(self):
        """상태바 설정"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready / 준비 완료")

    def _show_dashboard(self):
        self.dashboard.refresh()
        self.stack.setCurrentIndex(0)
        self.status_bar.showMessage("Dashboard / 대시보드")

    def _show_vmodel(self):
        if self.current_project_id:
            self.vmodel_view.load_project(self.current_project_id)
        self.stack.setCurrentIndex(2)
        self.status_bar.showMessage("V-Model View / V-모델 뷰")

    def _show_schedule(self):
        if self.current_project_id:
            self.schedule_view.load_project(self.current_project_id)
        self.stack.setCurrentIndex(4)
        self.status_bar.showMessage("Schedule / 일정 관리")

    def _show_trace_matrix(self):
        if self.current_project_id:
            self.trace_matrix.load_project(self.current_project_id)
        self.stack.setCurrentIndex(3)
        self.status_bar.showMessage("Traceability Matrix / 추적성 매트릭스")

    def _on_oem_selected(self, oem_id):
        self.status_bar.showMessage(f"OEM selected: {oem_id}")

    def _on_phase_selected(self, phase_id):
        """Handle phase selection from tree."""
        self.current_phase_id = phase_id
        from src.models.phase import PhaseModel
        phase = PhaseModel.get_by_id(phase_id)
        if phase:
            self.current_project_id = phase["project_id"]
            # Load vmodel/schedule/trace for the project (phase-filtered via stages)
            self.vmodel_view.load_project(phase["project_id"], phase_id=phase_id)
            self.stack.setCurrentIndex(2)
            self.status_bar.showMessage(
                f"Phase: {phase['name']} / 개발 단계 선택됨"
            )

    def _on_project_selected(self, project_id):
        self.current_project_id = project_id
        self.current_phase_id = None
        self.dashboard.load_project(project_id)
        self.stack.setCurrentIndex(0)
        self.status_bar.showMessage(f"Project loaded / 프로젝트 로드됨")

    def _on_stage_clicked(self, stage_id):
        self.current_stage_id = stage_id
        self.stage_detail.load_stage(stage_id)
        self.guide_panel.load_stage(stage_id)
        self.stack.setCurrentIndex(1)
        self.status_bar.showMessage(f"Stage detail / 단계 상세")

    def _new_project(self):
        from src.views.new_project_dialog import NewProjectDialog
        dialog = NewProjectDialog(self)
        if dialog.exec_():
            self.refresh_all()

    def _new_phase(self):
        """Open new phase dialog for current project."""
        if not self.current_project_id:
            QMessageBox.information(
                self, "No Project Selected",
                "Please select a project first.\n프로젝트를 먼저 선택해주세요."
            )
            return
        from src.views.new_phase_dialog import NewPhaseDialog
        dialog = NewPhaseDialog(self.current_project_id, parent=self)
        if dialog.exec_():
            self.refresh_all()

    def _manage_oems(self):
        dialog = OemConfigDialog(self)
        dialog.exec_()
        self.refresh_all()

    def _show_about(self):
        QMessageBox.about(
            self,
            "About ASPICE Process Manager",
            f"<h2>ASPICE Process Manager</h2>"
            f"<p>Version: {self.version}</p>"
            f"<p>ASPICE V-model 기반 소프트웨어 개발 프로세스 관리 도구</p>"
            f"<p>A tool for managing automotive software development processes "
            f"based on the ASPICE V-model.</p>"
            f"<hr>"
            f"<p>Python + PyQt5 + SQLite3</p>"
        )

    def _toggle_theme(self):
        """라이트/다크 테마 전환"""
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"
        QApplication.instance().setStyleSheet(get_stylesheet(self.current_theme))
        save_theme(self.current_theme)
        self.status_bar.showMessage(
            f"Theme changed to {self.current_theme} / 테마 변경: {self.current_theme}"
        )

    def _check_notifications(self):
        """시작 시 알림 확인 및 대시보드에 배너 표시"""
        try:
            summary = get_notification_summary()
            self.dashboard.update_notifications(
                summary.get("overdue", []),
                summary.get("upcoming", [])
            )
        except Exception:
            pass  # DB may not be initialized yet

    def _open_search(self):
        """Open search popup below the search input."""
        text = self.search_input.text().strip()
        if text:
            self.search_widget.search_input.setText(text)
            pos = self.search_input.mapToGlobal(
                QPoint(0, self.search_input.height())
            )
            self.search_widget.show_at(pos)

    def _on_search_result(self, result_type, result_id):
        """Handle search result click - navigate to the item."""
        if result_type == "document":
            from src.models.document import DocumentModel
            doc = DocumentModel.get_by_id(result_id)
            if doc:
                self._on_stage_clicked(doc["stage_id"])
        elif result_type == "checklist":
            conn = get_connection()
            item = conn.execute(
                "SELECT stage_id FROM checklist_items WHERE id = ?", (result_id,)
            ).fetchone()
            conn.close()
            if item:
                self._on_stage_clicked(item["stage_id"])
        self.status_bar.showMessage(f"Navigated to {result_type} #{result_id}")

    def _backup_database(self):
        """Backup SQLite database to a file."""
        from src.services.backup_service import backup_database
        path, _ = QFileDialog.getSaveFileName(
            self, "Backup Database", "", "SQLite Database (*.db);;All Files (*)"
        )
        if path:
            try:
                backup_database(path)
                QMessageBox.information(self, "Backup", f"Database backed up to:\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Backup Error", str(e))

    def _restore_database(self):
        """Restore SQLite database from a backup file."""
        from src.services.backup_service import restore_database
        path, _ = QFileDialog.getOpenFileName(
            self, "Restore Database", "", "SQLite Database (*.db);;All Files (*)"
        )
        if path:
            reply = QMessageBox.question(
                self, "Restore Database",
                "This will replace the current database with the backup.\n"
                "All current data will be lost. Continue?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    restore_database(path)
                    QMessageBox.information(
                        self, "Restore",
                        "Database restored successfully.\nPlease restart the application."
                    )
                    self.refresh_all()
                except Exception as e:
                    QMessageBox.warning(self, "Restore Error", str(e))

    def _export_json(self):
        """Export all data as JSON."""
        from src.services.backup_service import export_to_json
        path, _ = QFileDialog.getSaveFileName(
            self, "Export as JSON", "", "JSON Files (*.json);;All Files (*)"
        )
        if path:
            try:
                export_to_json(path)
                QMessageBox.information(self, "Export", f"Data exported to:\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))

    def _import_json(self):
        """Import data from JSON file."""
        from src.services.backup_service import import_from_json
        path, _ = QFileDialog.getOpenFileName(
            self, "Import from JSON", "", "JSON Files (*.json);;All Files (*)"
        )
        if path:
            reply = QMessageBox.question(
                self, "Import from JSON",
                "This will replace ALL current data with the imported data.\n"
                "All current data will be lost. Continue?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    import_from_json(path)
                    QMessageBox.information(self, "Import", "Data imported successfully.")
                    self.refresh_all()
                except Exception as e:
                    QMessageBox.warning(self, "Import Error", str(e))

    def _generate_aspice_report(self):
        """Generate ASPICE compliance report as HTML file."""
        if not self.current_project_id:
            QMessageBox.information(
                self, "No Project Selected",
                "Please select a project first.\n프로젝트를 먼저 선택해주세요."
            )
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save ASPICE Report / ASPICE 보고서 저장",
            "", "HTML Files (*.html);;All Files (*)"
        )
        if path:
            try:
                from src.services.compliance_report_service import generate_compliance_report
                generate_compliance_report(
                    self.current_project_id,
                    phase_id=self.current_phase_id,
                    output_path=path,
                )
                QMessageBox.information(
                    self, "Report Generated / 보고서 생성 완료",
                    f"ASPICE compliance report saved to:\n"
                    f"ASPICE 준수 보고서 저장 완료:\n{path}"
                )
                self.status_bar.showMessage(
                    "ASPICE report generated / ASPICE 보고서 생성 완료"
                )
            except Exception as e:
                QMessageBox.warning(
                    self, "Report Error / 보고서 오류", str(e)
                )

    def _reset_demo_data(self):
        """DB 삭제 후 데모 데이터 재생성"""
        reply = QMessageBox.question(
            self, "Reset Demo Data / 데모 초기화",
            "This will DELETE all current data and recreate demo projects.\n"
            "현재 모든 데이터를 삭제하고 데모 프로젝트를 다시 생성합니다.\n\n"
            "Proceed / 진행하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        import os
        from src.models.database import DB_PATH, initialize_schema
        from src.services.demo_data_service import create_demo_data
        try:
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            conn = get_connection()
            initialize_schema(conn)
            create_demo_data(conn)
            conn.close()
            self.current_project_id = None
            self.current_phase_id = None
            self.refresh_all()
            self._show_dashboard()
            QMessageBox.information(self, "Success", "Demo data has been reset.\n데모 데이터가 초기화되었습니다.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to reset: {e}")

    def refresh_all(self):
        """전체 새로고침"""
        self.project_tree.refresh()
        self.dashboard.refresh()
        if self.current_project_id:
            self.dashboard.load_project(self.current_project_id)
        self._check_notifications()
