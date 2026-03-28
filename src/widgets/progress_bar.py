"""커스텀 진행바 위젯"""
from PyQt5.QtWidgets import QProgressBar


class StageProgressBar(QProgressBar):
    """단계 완료 진행바"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(8)
        self.setTextVisible(False)
