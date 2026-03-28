"""첨부파일 관리 위젯"""
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices

from src.models.attachment import AttachmentModel
from src.models.database import get_connection


class AttachmentWidget(QWidget):
    """첨부파일 관리 위젯"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stage_id = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 상단 버튼
        top_bar = QHBoxLayout()
        self.btn_attach = QPushButton("Attach File / 파일 첨부")
        self.btn_attach.clicked.connect(self._on_attach)
        top_bar.addWidget(self.btn_attach)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # 파일 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "File Name / 파일명", "Type / 유형", "Description / 설명",
            "Size / 크기", "Date / 일자", "", ""
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        for col in [1, 3, 4, 5, 6]:
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

    def load_stage(self, stage_id, conn=None):
        """단계의 첨부파일 로드"""
        self.stage_id = stage_id
        should_close = conn is None
        if conn is None:
            conn = get_connection()

        attachments = AttachmentModel.get_by_stage(stage_id, conn)
        self.table.setRowCount(len(attachments))

        for i, att in enumerate(attachments):
            self.table.setItem(i, 0, QTableWidgetItem(att["file_name"]))
            self.table.setItem(i, 1, QTableWidgetItem(att["file_type"] or ""))
            self.table.setItem(i, 2, QTableWidgetItem(att["description"] or ""))
            self.table.setItem(i, 3, QTableWidgetItem(self._format_size(att["file_size"])))
            self.table.setItem(i, 4, QTableWidgetItem(
                (att["created_at"] or "")[:10] if att["created_at"] else ""
            ))

            # Open button
            btn_open = QPushButton("Open / 열기")
            btn_open.clicked.connect(
                lambda checked, path=att["file_path"]: self._open_file(path)
            )
            self.table.setCellWidget(i, 5, btn_open)

            # Delete button
            btn_del = QPushButton("Remove / 삭제")
            btn_del.clicked.connect(
                lambda checked, aid=att["id"]: self._delete_attachment(aid)
            )
            self.table.setCellWidget(i, 6, btn_del)

        if should_close:
            conn.close()

    def _format_size(self, size_bytes):
        """파일 크기를 사람이 읽기 쉬운 형식으로 변환"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _on_attach(self):
        """파일 첨부"""
        if not self.stage_id:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File / 파일 선택", "",
            "All Files (*)"
        )
        if not file_path:
            return

        # 설명 입력
        description, ok = QInputDialog.getText(
            self, "Description / 설명",
            "Enter file description / 파일 설명을 입력하세요:"
        )
        if not ok:
            return

        file_name = os.path.basename(file_path)
        _, ext = os.path.splitext(file_name)
        file_type = ext.lstrip(".").upper() if ext else ""

        try:
            file_size = os.path.getsize(file_path)
        except OSError:
            file_size = 0

        AttachmentModel.create(
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            description=description,
            file_size=file_size,
            stage_id=self.stage_id,
        )
        self.load_stage(self.stage_id)

    def _open_file(self, file_path):
        """파일 열기"""
        if file_path and os.path.exists(file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        else:
            QMessageBox.warning(
                self, "File Not Found / 파일 없음",
                f"Cannot find file:\n{file_path}"
            )

    def _delete_attachment(self, attachment_id):
        """첨부파일 삭제"""
        reply = QMessageBox.question(
            self, "Confirm Delete / 삭제 확인",
            "Remove this attachment? / 이 첨부파일을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            AttachmentModel.delete(attachment_id)
            self.load_stage(self.stage_id)
