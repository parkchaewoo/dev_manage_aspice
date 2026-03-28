"""V-Model 다이어그램 뷰"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsView,
    QGraphicsScene, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPen, QColor, QPainter, QFont

from src.models.database import get_connection
from src.models.stage import StageModel
from src.models.project import ProjectModel
from src.models.oem import OemModel
from src.models.traceability import TraceabilityModel
from src.models.document import DocumentModel
from src.utils.constants import SWE_STAGES, VMODEL_PAIRS, SEQUENTIAL_PAIRS
from src.widgets.clickable_node import ClickableNode
from src.widgets.trace_line import TraceLine


class VModelWidget(QWidget):
    stage_clicked = pyqtSignal(int)

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
        self.title_label = QLabel("V-Model View / V-모델 뷰")
        self.title_label.setProperty("heading", True)
        header.addWidget(self.title_label)
        header.addStretch()

        # 범례
        legend = QHBoxLayout()
        legend.setSpacing(16)
        for label, color in [
            ("Not Started", "#8E8E93"), ("In Progress", "#007AFF"),
            ("In Review", "#FF9500"), ("Completed", "#34C759")
        ]:
            dot = QLabel(f"● {label}")
            dot.setStyleSheet(f"color: {color}; font-size: 11px;")
            legend.addWidget(dot)
        header.addLayout(legend)
        layout.addLayout(header)

        # 그래픽스 뷰
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setStyleSheet("background-color: #FAFAFA; border: 1px solid #E5E5EA; border-radius: 12px;")
        layout.addWidget(self.view, 1)

        # 하단 힌트
        hint = QLabel(
            "Click a stage to view details / 단계를 클릭하면 상세 정보를 볼 수 있습니다  |  "
            "Click a trace line to see document connections / 추적성 라인을 클릭하면 문서 연결을 볼 수 있습니다"
        )
        hint.setProperty("caption", True)
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

    def load_project(self, project_id, phase_id=None):
        """프로젝트의 V-model 다이어그램 로드"""
        self.project_id = project_id
        self.scene.clear()

        conn = get_connection()
        project = ProjectModel.get_by_id(project_id, conn)
        if not project:
            conn.close()
            return

        oem = OemModel.get_by_id(project["oem_id"], conn)

        if phase_id:
            from src.models.phase import PhaseModel
            phase = PhaseModel.get_by_id(phase_id, conn)
            phase_name = phase["name"] if phase else ""
            self.title_label.setText(
                f"V-Model: {oem['name']} > {project['name']} > {phase_name}"
            )
        else:
            self.title_label.setText(
                f"V-Model: {oem['name']} > {project['name']}"
            )

        if phase_id:
            stages = StageModel.get_by_phase(phase_id, conn)
        else:
            stages = StageModel.get_by_project(project_id, conn)
        stage_map = {s["swe_level"]: s for s in stages}

        # V자 배치 좌표
        node_w, node_h = 220, 85
        positions = {
            "SWE.1": (50, 40),
            "SWE.2": (170, 200),
            "SWE.3": (290, 360),
            "SWE.4": (530, 360),
            "SWE.5": (650, 200),
            "SWE.6": (770, 40),
        }

        nodes = {}

        # 노드 생성
        for swe, pos in positions.items():
            stage = stage_map.get(swe)
            if not stage:
                continue

            info = SWE_STAGES[swe]
            stats = StageModel.get_completion_stats(stage["id"], conn)
            doc_count = stats["doc_total"]

            node = ClickableNode(
                swe_level=swe,
                name=info["name_ko"],
                status=stage["status"],
                doc_count=doc_count,
                completion_pct=stats["overall_pct"],
                x=pos[0], y=pos[1],
                width=node_w, height=node_h,
                callback=lambda sid: self.stage_clicked.emit(sid),
                stage_id=stage["id"],
            )
            node.setZValue(10)  # 노드를 라인보다 앞에 표시
            self.scene.addItem(node)
            nodes[swe] = (node, stage)

        # 순차적 추적성 라인 (SWE.1→SWE.2, SWE.2→SWE.3: derives 관계)
        for src_swe, dst_swe in SEQUENTIAL_PAIRS.items():
            src_stage = stage_map.get(src_swe)
            dst_stage = stage_map.get(dst_swe)
            if src_stage and dst_stage and src_swe in positions and dst_swe in positions:
                sx, sy = positions[src_swe]
                dx, dy = positions[dst_swe]
                completeness = TraceabilityModel.get_completeness_for_pair(
                    src_stage["id"], dst_stage["id"], conn
                )
                trace = TraceLine(
                    sx + node_w / 2, sy + node_h,
                    dx + node_w / 2, dy,
                    link_count=completeness["link_count"],
                    completeness_pct=completeness["completeness_pct"],
                    callback=self._on_trace_clicked,
                    stage_ids=(src_stage["id"], dst_stage["id"]),
                )
                self.scene.addItem(trace)
            elif src_swe in positions and dst_swe in positions:
                sx, sy = positions[src_swe]
                dx, dy = positions[dst_swe]
                self.scene.addLine(
                    sx + node_w / 2, sy + node_h,
                    dx + node_w / 2, dy,
                    QPen(QColor("#C7C7CC"), 2, Qt.SolidLine)
                )

        # V-model 쌍 추적성 라인
        for left_swe, right_swe in VMODEL_PAIRS.items():
            left = stage_map.get(left_swe)
            right = stage_map.get(right_swe)
            if not left or not right:
                continue

            completeness = TraceabilityModel.get_completeness_for_pair(
                left["id"], right["id"], conn
            )

            lx, ly = positions[left_swe]
            rx, ry = positions[right_swe]

            trace = TraceLine(
                lx + node_w, ly + node_h / 2,
                rx, ry + node_h / 2,
                link_count=completeness["link_count"],
                completeness_pct=completeness["completeness_pct"],
                callback=self._on_trace_clicked,
                stage_ids=(left["id"], right["id"]),
            )
            self.scene.addItem(trace)

        # 타이틀 텍스트
        title_text = self.scene.addText(
            "Development / 개발", QFont("sans-serif", 10)
        )
        title_text.setDefaultTextColor(QColor("#8E8E93"))
        title_text.setPos(50, 10)

        verify_text = self.scene.addText(
            "Verification / 검증", QFont("sans-serif", 10)
        )
        verify_text.setDefaultTextColor(QColor("#8E8E93"))
        verify_text.setPos(770, 10)

        # SWE.3→SWE.4 중간 텍스트
        impl_text = self.scene.addText(
            "Implementation\n구현", QFont("sans-serif", 9)
        )
        impl_text.setDefaultTextColor(QColor("#C7C7CC"))
        impl_text.setPos(400, 380)

        conn.close()

        # 전체 장면에 맞추기
        if self.scene.items():
            self.view.fitInView(self.scene.sceneRect().adjusted(-30, -30, 30, 30), Qt.KeepAspectRatio)

    def _on_trace_clicked(self, stage_id_1, stage_id_2):
        """추적성 라인 클릭 시 상세 뷰"""
        from src.views.traceability_detail import TraceabilityDetailDialog
        dialog = TraceabilityDetailDialog(stage_id_1, stage_id_2, self)
        dialog.exec_()

    def wheelEvent(self, event):
        """마우스 휠로 줌 인/아웃"""
        factor = 1.15
        if event.angleDelta().y() > 0:
            self.view.scale(factor, factor)
        else:
            self.view.scale(1 / factor, 1 / factor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene.items():
            self.view.fitInView(
                self.scene.sceneRect().adjusted(-30, -30, 30, 30),
                Qt.KeepAspectRatio
            )
