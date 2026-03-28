"""새 프로젝트 생성 다이얼로그"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QHBoxLayout, QDateEdit, QMessageBox
)
from PyQt5.QtCore import QDate

from src.models.database import get_connection
from src.models.oem import OemModel
from src.services.project_service import create_project_from_template


class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project / 새 프로젝트")
        self.setMinimumWidth(450)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(14)

        # OEM 선택
        self.oem_combo = QComboBox()
        conn = get_connection()
        oems = OemModel.get_all(conn)
        conn.close()
        for oem in oems:
            self.oem_combo.addItem(oem["name"], oem["id"])
        layout.addRow("OEM:", self.oem_combo)

        # 프로젝트 이름
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Project name / 프로젝트 이름")
        layout.addRow("Name / 이름:", self.name_edit)

        # 설명
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Description / 설명")
        layout.addRow("Description / 설명:", self.desc_edit)

        # 시작일
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        layout.addRow("Start Date / 시작일:", self.start_date)

        # 목표 종료일
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addMonths(6))
        self.end_date.setCalendarPopup(True)
        layout.addRow("Target End / 목표 종료일:", self.end_date)

        # 버튼
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel / 취소")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        create_btn = QPushButton("Create / 생성")
        create_btn.clicked.connect(self._create)
        btn_layout.addWidget(create_btn)
        layout.addRow(btn_layout)

    def _create(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a project name.\n프로젝트 이름을 입력해주세요.")
            return

        oem_id = self.oem_combo.currentData()
        if not oem_id:
            QMessageBox.warning(self, "Error", "Please select an OEM.\nOEM을 선택해주세요.")
            return

        conn = get_connection()
        try:
            create_project_from_template(
                oem_id=oem_id,
                project_name=name,
                description=self.desc_edit.text(),
                start_date=self.start_date.date().toString("yyyy-MM-dd"),
                target_end_date=self.end_date.date().toString("yyyy-MM-dd"),
                conn=conn
            )
            conn.close()
            self.accept()
        except Exception as e:
            conn.close()
            QMessageBox.critical(self, "Error", f"Failed to create project:\n{e}")
