"""체크리스트 위젯"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QProgressBar, QPushButton, QLineEdit, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt

from src.models.checklist import ChecklistModel


class ChecklistWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stage_id = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 헤더
        header = QHBoxLayout()
        header.addWidget(QLabel("Checklist / 체크리스트"))
        header.addStretch()

        self.progress_label = QLabel("0/0")
        self.progress_label.setProperty("caption", True)
        header.addWidget(self.progress_label)
        layout.addLayout(header)

        # 진행바
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(8)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_widget = QWidget()
        self.items_layout = QVBoxLayout(scroll_widget)
        self.items_layout.setSpacing(4)
        self.items_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)

        # 추가 영역
        add_layout = QHBoxLayout()
        self.add_input = QLineEdit()
        self.add_input.setPlaceholderText("New item... / 새 항목...")
        self.add_input.returnPressed.connect(self._add_item)
        add_layout.addWidget(self.add_input)

        self.btn_add = QPushButton("+ Add")
        self.btn_add.setProperty("secondary", True)
        self.btn_add.setMaximumWidth(80)
        self.btn_add.clicked.connect(self._add_item)
        add_layout.addWidget(self.btn_add)
        layout.addLayout(add_layout)

    def load_stage(self, stage_id, conn=None):
        """단계의 체크리스트 로드"""
        self.stage_id = stage_id
        from src.models.database import get_connection
        should_close = conn is None
        if conn is None:
            conn = get_connection()

        items = ChecklistModel.get_by_stage(stage_id, conn)
        self._clear_items()

        total = len(items)
        checked = sum(1 for item in items if item["is_checked"])

        for item in items:
            self._add_check_row(item)

        self._update_progress(checked, total)
        if should_close:
            conn.close()

    def _add_check_row(self, item):
        """체크리스트 행 추가"""
        row = QHBoxLayout()

        cb = QCheckBox(item["description"])
        cb.setChecked(bool(item["is_checked"]))
        if item["is_checked"]:
            cb.setStyleSheet("text-decoration: line-through; color: #8E8E93;")
        cb.stateChanged.connect(lambda state, iid=item["id"]: self._toggle_item(iid, state))
        row.addWidget(cb, 1)

        del_btn = QPushButton("x")
        del_btn.setMaximumSize(28, 28)
        del_btn.setStyleSheet(
            "background-color: transparent; color: #FF3B30; "
            "border: none; font-weight: bold; font-size: 14px;"
        )
        del_btn.clicked.connect(lambda _, iid=item["id"]: self._delete_item(iid))
        row.addWidget(del_btn)

        # stretch 전에 삽입
        idx = self.items_layout.count() - 1
        self.items_layout.insertLayout(idx, row)

    def _toggle_item(self, item_id, state):
        ChecklistModel.toggle(item_id)
        self.load_stage(self.stage_id)

    def _add_item(self):
        text = self.add_input.text().strip()
        if text and self.stage_id:
            ChecklistModel.create(self.stage_id, text)
            self.add_input.clear()
            self.load_stage(self.stage_id)

    def _delete_item(self, item_id):
        ChecklistModel.delete(item_id)
        self.load_stage(self.stage_id)

    def _update_progress(self, checked, total):
        pct = int(checked / total * 100) if total > 0 else 0
        self.progress_bar.setValue(pct)
        self.progress_label.setText(f"{checked}/{total} ({pct}%)")

    def _clear_items(self):
        while self.items_layout.count() > 1:
            item = self.items_layout.takeAt(0)
            if item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
