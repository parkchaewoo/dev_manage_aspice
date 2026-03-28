"""새 개발 단계(Phase) 생성 다이얼로그"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QHBoxLayout, QMessageBox, QRadioButton,
    QButtonGroup, QGroupBox, QLabel
)
from PyQt5.QtCore import Qt

from src.models.database import get_connection
from src.models.phase import PhaseModel
from src.models.project import ProjectModel
from src.models.oem import OemModel
from src.utils.yaml_helpers import load_yaml_string

_CUSTOM_OPTION = "Custom... / 직접 입력..."


class NewPhaseDialog(QDialog):
    def __init__(self, project_id, inherit_from_phase_id=None, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.inherit_from_phase_id = inherit_from_phase_id
        self.setWindowTitle("New Phase / 새 개발 단계")
        self.setMinimumWidth(450)
        self._oem_phases = []
        self._existing_phase_names = []
        self._load_oem_phases()
        self._setup_ui()

    def _load_oem_phases(self):
        """Load OEM-defined phases from the project's OEM config."""
        conn = get_connection()
        try:
            project = ProjectModel.get_by_id(self.project_id, conn)
            if project:
                oem = OemModel.get_by_id(project["oem_id"], conn)
                if oem and oem["config_yaml"]:
                    try:
                        config = load_yaml_string(oem["config_yaml"])
                        if config and isinstance(config, dict):
                            phases = config.get("phases", [])
                            if isinstance(phases, list):
                                self._oem_phases = [str(p) for p in phases]
                    except Exception:
                        pass

            # Load existing phase names to disable them
            existing_phases = PhaseModel.get_by_project(self.project_id, conn)
            self._existing_phase_names = [p["name"] for p in existing_phases]
        finally:
            conn.close()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(10)

        # Phase name - QComboBox with OEM-defined phases
        self.name_combo = QComboBox()
        self.name_combo.setEditable(False)
        for phase_name in self._oem_phases:
            self.name_combo.addItem(phase_name)
        self.name_combo.addItem(_CUSTOM_OPTION)

        # Disable phases that already exist in the project
        for i in range(self.name_combo.count()):
            item_text = self.name_combo.itemText(i)
            if item_text in self._existing_phase_names and item_text != _CUSTOM_OPTION:
                # Disable the item by setting its flags
                model = self.name_combo.model()
                item = model.item(i)
                if item:
                    item.setEnabled(False)

        self.name_combo.currentIndexChanged.connect(self._on_name_combo_changed)
        form.addRow("Name / 이름:", self.name_combo)

        # Custom name input (hidden by default)
        self.custom_name_edit = QLineEdit()
        self.custom_name_edit.setPlaceholderText("Custom phase name / 사용자 정의 단계 이름")
        self.custom_name_edit.setVisible(False)
        form.addRow("", self.custom_name_edit)

        # Description
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Description / 설명")
        form.addRow("Description / 설명:", self.desc_edit)

        layout.addLayout(form)

        # Creation mode
        mode_group = QGroupBox("Creation Mode / 생성 방식")
        mode_layout = QVBoxLayout(mode_group)

        self.btn_group = QButtonGroup(self)
        self.radio_empty = QRadioButton("Create Empty / 빈 단계 생성")
        self.radio_inherit = QRadioButton("Inherit from Previous Phase / 이전 단계에서 상속")

        self.btn_group.addButton(self.radio_empty, 0)
        self.btn_group.addButton(self.radio_inherit, 1)

        mode_layout.addWidget(self.radio_empty)
        mode_layout.addWidget(self.radio_inherit)

        # Source phase dropdown
        self.source_label = QLabel("Source Phase / 원본 단계:")
        self.source_combo = QComboBox()
        self._load_phases()

        mode_layout.addWidget(self.source_label)
        mode_layout.addWidget(self.source_combo)

        layout.addWidget(mode_group)

        # Set default mode
        if self.inherit_from_phase_id:
            self.radio_inherit.setChecked(True)
            # Select the source phase
            for i in range(self.source_combo.count()):
                if self.source_combo.itemData(i) == self.inherit_from_phase_id:
                    self.source_combo.setCurrentIndex(i)
                    break
        else:
            self.radio_empty.setChecked(True)

        self._update_inherit_visibility()
        self.btn_group.buttonClicked.connect(lambda: self._update_inherit_visibility())

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel / 취소")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        create_btn = QPushButton("Create / 생성")
        create_btn.clicked.connect(self._create)
        btn_layout.addWidget(create_btn)
        layout.addLayout(btn_layout)

    def _on_name_combo_changed(self, index):
        """Show/hide custom name input based on combo selection."""
        is_custom = self.name_combo.currentText() == _CUSTOM_OPTION
        self.custom_name_edit.setVisible(is_custom)

    def _load_phases(self):
        """Load existing phases for the project."""
        conn = get_connection()
        phases = PhaseModel.get_by_project(self.project_id, conn)
        conn.close()
        for phase in phases:
            self.source_combo.addItem(
                f"{phase['name']} (#{phase['id']})", phase["id"]
            )

    def _update_inherit_visibility(self):
        """Show/hide source phase selector based on mode."""
        is_inherit = self.radio_inherit.isChecked()
        self.source_label.setVisible(is_inherit)
        self.source_combo.setVisible(is_inherit)

    def _create(self):
        if self.name_combo.currentText() == _CUSTOM_OPTION:
            name = self.custom_name_edit.text().strip()
        else:
            name = self.name_combo.currentText().strip()
        if not name:
            QMessageBox.warning(
                self, "Error",
                "Please enter a phase name.\n단계 이름을 입력해주세요."
            )
            return

        conn = get_connection()
        try:
            if self.radio_inherit.isChecked():
                source_phase_id = self.source_combo.currentData()
                if source_phase_id is None:
                    QMessageBox.warning(
                        self, "Error",
                        "Please select a source phase.\n원본 단계를 선택해주세요."
                    )
                    conn.close()
                    return
                from src.services.phase_service import create_phase_inherited
                create_phase_inherited(
                    self.project_id, name, source_phase_id,
                    description=self.desc_edit.text(), conn=conn
                )
            else:
                from src.services.phase_service import create_phase_from_template
                create_phase_from_template(
                    self.project_id, name,
                    description=self.desc_edit.text(), conn=conn
                )
            conn.close()
            self.accept()
        except Exception as e:
            conn.close()
            QMessageBox.critical(
                self, "Error", f"Failed to create phase:\n{e}"
            )
