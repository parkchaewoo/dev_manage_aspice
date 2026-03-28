"""OEM 설정 관리 다이얼로그"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QPushButton, QLineEdit, QTextEdit, QTabWidget, QWidget,
    QFormLayout, QListWidgetItem, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt

from src.models.database import get_connection
from src.models.oem import OemModel
from src.utils.yaml_helpers import load_yaml_string, dump_yaml_string


class OemConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OEM Management / OEM 관리")
        self.setMinimumSize(700, 500)
        self._setup_ui()
        self._load_oems()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(16)

        # 좌측: OEM 목록
        left = QVBoxLayout()
        left.addWidget(QLabel("OEMs"))

        self.oem_list = QListWidget()
        self.oem_list.currentRowChanged.connect(self._on_oem_selected)
        left.addWidget(self.oem_list)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("+ Add")
        self.btn_add.setProperty("secondary", True)
        self.btn_add.clicked.connect(self._add_oem)
        btn_layout.addWidget(self.btn_add)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setProperty("danger", True)
        self.btn_delete.clicked.connect(self._delete_oem)
        btn_layout.addWidget(self.btn_delete)
        left.addLayout(btn_layout)

        layout.addLayout(left, 1)

        # 우측: OEM 상세
        right = QVBoxLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("OEM Name / OEM 이름")
        right.addWidget(QLabel("Name / 이름:"))
        right.addWidget(self.name_edit)

        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Description / 설명")
        right.addWidget(QLabel("Description / 설명:"))
        right.addWidget(self.desc_edit)

        right.addWidget(QLabel("Configuration (YAML):"))
        self.config_edit = QTextEdit()
        self.config_edit.setPlaceholderText(
            "OEM specific YAML configuration...\n"
            "OEM별 YAML 설정을 여기에 입력하세요..."
        )
        right.addWidget(self.config_edit)

        self.btn_save = QPushButton("Save / 저장")
        self.btn_save.clicked.connect(self._save_oem)
        right.addWidget(self.btn_save)

        layout.addLayout(right, 2)

    def _load_oems(self):
        self.oem_list.clear()
        conn = get_connection()
        self.oems = OemModel.get_all(conn)
        conn.close()

        for oem in self.oems:
            self.oem_list.addItem(oem["name"])

    def _on_oem_selected(self, row):
        if 0 <= row < len(self.oems):
            oem = self.oems[row]
            self.name_edit.setText(oem["name"])
            self.desc_edit.setText(oem["description"] or "")
            self.config_edit.setText(oem["config_yaml"] or "")

    def _add_oem(self):
        conn = get_connection()
        OemModel.create("New OEM", "Description", "", conn)
        conn.close()
        self._load_oems()
        self.oem_list.setCurrentRow(self.oem_list.count() - 1)

    def _save_oem(self):
        row = self.oem_list.currentRow()
        if row < 0:
            return

        oem = self.oems[row]
        config_text = self.config_edit.toPlainText()

        # YAML 유효성 검사
        if config_text.strip():
            try:
                load_yaml_string(config_text)
            except Exception as e:
                QMessageBox.warning(self, "Invalid YAML", f"YAML syntax error:\n{e}")
                return

        conn = get_connection()
        OemModel.update(
            oem["id"],
            name=self.name_edit.text(),
            description=self.desc_edit.text(),
            config_yaml=config_text,
            conn=conn
        )
        conn.close()
        self._load_oems()

    def _delete_oem(self):
        row = self.oem_list.currentRow()
        if row < 0:
            return

        reply = QMessageBox.question(
            self, "Delete OEM",
            f"Delete '{self.oems[row]['name']}' and all its projects?\n"
            f"'{self.oems[row]['name']}'과(와) 모든 프로젝트를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            OemModel.delete(self.oems[row]["id"])
            self._load_oems()
