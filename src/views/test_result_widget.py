"""시험 결과 위젯"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QSpinBox, QDoubleSpinBox, QDialogButtonBox, QTextEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont

from src.models.test_result import TestResultModel
from src.models.database import get_connection


class TestResultAddDialog(QDialog):
    """시험 실행 결과 추가 다이얼로그"""

    def __init__(self, stage_id, parent=None):
        super().__init__(parent)
        self.stage_id = stage_id
        self.setWindowTitle("Add Test Run / 시험 실행 추가")
        self.setMinimumWidth(460)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        # Test Date / 시험 일자
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form.addRow("Test Date / 시험 일자:", self.date_edit)

        # Test Type / 시험 유형
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.addItems(["Unit Test", "Integration Test", "Qualification Test", "Regression"])
        form.addRow("Test Type / 시험 유형:", self.type_combo)

        # Total Cases / 전체 케이스
        self.total_spin = QSpinBox()
        self.total_spin.setRange(0, 999999)
        form.addRow("Total Cases / 전체 케이스:", self.total_spin)

        # Passed / 통과
        self.passed_spin = QSpinBox()
        self.passed_spin.setRange(0, 999999)
        form.addRow("Passed / 통과:", self.passed_spin)

        # Failed / 실패
        self.failed_spin = QSpinBox()
        self.failed_spin.setRange(0, 999999)
        form.addRow("Failed / 실패:", self.failed_spin)

        # Blocked / 차단
        self.blocked_spin = QSpinBox()
        self.blocked_spin.setRange(0, 999999)
        form.addRow("Blocked / 차단:", self.blocked_spin)

        # Coverage - Statement
        self.cov_statement = QDoubleSpinBox()
        self.cov_statement.setRange(0, 100)
        self.cov_statement.setSuffix(" %")
        self.cov_statement.setDecimals(1)
        form.addRow("Coverage Statement / 구문 커버리지:", self.cov_statement)

        # Coverage - Branch
        self.cov_branch = QDoubleSpinBox()
        self.cov_branch.setRange(0, 100)
        self.cov_branch.setSuffix(" %")
        self.cov_branch.setDecimals(1)
        form.addRow("Coverage Branch / 분기 커버리지:", self.cov_branch)

        # Coverage - MC/DC
        self.cov_mcdc = QDoubleSpinBox()
        self.cov_mcdc.setRange(0, 100)
        self.cov_mcdc.setSuffix(" %")
        self.cov_mcdc.setDecimals(1)
        form.addRow("Coverage MC/DC:", self.cov_mcdc)

        # Tool Name / 도구명
        self.tool_name_edit = QLineEdit()
        self.tool_name_edit.setPlaceholderText("e.g. VectorCAST, GoogleTest")
        form.addRow("Tool Name / 도구명:", self.tool_name_edit)

        # Tool Version / 도구 버전
        self.tool_version_edit = QLineEdit()
        form.addRow("Tool Version / 도구 버전:", self.tool_version_edit)

        # Notes / 비고
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Additional notes / 추가 메모")
        form.addRow("Notes / 비고:", self.notes_edit)

        layout.addLayout(form)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        btn_box.accepted.connect(self._save)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _save(self):
        total = self.total_spin.value()
        passed = self.passed_spin.value()
        failed = self.failed_spin.value()
        blocked = self.blocked_spin.value()
        not_executed = max(0, total - passed - failed - blocked)
        pass_rate = (passed / total * 100) if total > 0 else 0

        TestResultModel.create(
            stage_id=self.stage_id,
            test_date=self.date_edit.date().toString("yyyy-MM-dd"),
            test_type=self.type_combo.currentText(),
            total_cases=total,
            passed=passed,
            failed=failed,
            blocked=blocked,
            not_executed=not_executed,
            pass_rate=round(pass_rate, 1),
            coverage_statement=self.cov_statement.value(),
            coverage_branch=self.cov_branch.value(),
            coverage_mcdc=self.cov_mcdc.value(),
            tool_name=self.tool_name_edit.text(),
            tool_version=self.tool_version_edit.text(),
            notes=self.notes_edit.text(),
        )
        self.accept()


class TestResultWidget(QWidget):
    """시험 결과 표시 위젯"""

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
        self.btn_add = QPushButton("Add Test Run / 시험 실행 추가")
        self.btn_add.clicked.connect(self._on_add)
        top_bar.addWidget(self.btn_add)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # 최신 결과 요약 프레임
        self.summary_frame = QFrame()
        self.summary_frame.setProperty("card", True)
        summary_layout = QHBoxLayout(self.summary_frame)

        self.lbl_pass_rate = self._summary_card("Pass Rate\n통과율", "- %", "#34C759")
        self.lbl_total = self._summary_card("Total\n전체", "-", "#007AFF")
        self.lbl_passed = self._summary_card("Passed\n통과", "-", "#34C759")
        self.lbl_failed = self._summary_card("Failed\n실패", "-", "#FF3B30")
        self.lbl_cov_stmt = self._summary_card("Statement\n구문", "- %", "#5856D6")
        self.lbl_cov_branch = self._summary_card("Branch\n분기", "- %", "#5856D6")
        self.lbl_cov_mcdc = self._summary_card("MC/DC", "- %", "#5856D6")

        for card in [self.lbl_pass_rate, self.lbl_total, self.lbl_passed,
                     self.lbl_failed, self.lbl_cov_stmt, self.lbl_cov_branch, self.lbl_cov_mcdc]:
            summary_layout.addWidget(card)

        layout.addWidget(self.summary_frame)

        # 이력 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Date / 일자", "Type / 유형", "Total", "Pass", "Fail",
            "Pass Rate", "Stmt %", "Branch %", "MC/DC %"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

    def _summary_card(self, title, value, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ background-color: {color}15; border-radius: 8px; padding: 6px; }}
        """)
        vl = QVBoxLayout(frame)
        vl.setContentsMargins(10, 6, 10, 6)

        val_lbl = QLabel(value)
        val_lbl.setAlignment(Qt.AlignCenter)
        val_lbl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        val_lbl.setObjectName("value")
        vl.addWidget(val_lbl)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet("font-size: 10px; color: #666;")
        vl.addWidget(title_lbl)

        return frame

    def _update_card_value(self, card_frame, text):
        for child in card_frame.findChildren(QLabel):
            if child.objectName() == "value":
                child.setText(str(text))
                break

    def load_stage(self, stage_id, conn=None):
        """단계의 시험 결과 로드"""
        self.stage_id = stage_id
        should_close = conn is None
        if conn is None:
            conn = get_connection()

        # 최신 결과 요약
        latest = TestResultModel.get_latest_by_stage(stage_id, conn)
        if latest:
            self._update_card_value(self.lbl_pass_rate, f"{latest['pass_rate']:.1f}%")
            self._update_card_value(self.lbl_total, str(latest["total_cases"]))
            self._update_card_value(self.lbl_passed, str(latest["passed"]))
            self._update_card_value(self.lbl_failed, str(latest["failed"]))
            self._update_card_value(self.lbl_cov_stmt, f"{latest['coverage_statement']:.1f}%")
            self._update_card_value(self.lbl_cov_branch, f"{latest['coverage_branch']:.1f}%")
            self._update_card_value(self.lbl_cov_mcdc, f"{latest['coverage_mcdc']:.1f}%")
        else:
            for card in [self.lbl_pass_rate, self.lbl_cov_stmt, self.lbl_cov_branch, self.lbl_cov_mcdc]:
                self._update_card_value(card, "- %")
            for card in [self.lbl_total, self.lbl_passed, self.lbl_failed]:
                self._update_card_value(card, "-")

        # 이력 테이블
        results = TestResultModel.get_by_stage(stage_id, conn)
        self.table.setRowCount(len(results))
        for i, r in enumerate(results):
            self.table.setItem(i, 0, QTableWidgetItem(r["test_date"] or ""))
            self.table.setItem(i, 1, QTableWidgetItem(r["test_type"] or ""))
            self.table.setItem(i, 2, QTableWidgetItem(str(r["total_cases"])))
            self.table.setItem(i, 3, QTableWidgetItem(str(r["passed"])))
            self.table.setItem(i, 4, QTableWidgetItem(str(r["failed"])))

            rate_item = QTableWidgetItem(f"{r['pass_rate']:.1f}%")
            if r["pass_rate"] >= 95:
                rate_item.setForeground(QColor("#34C759"))
            elif r["pass_rate"] >= 80:
                rate_item.setForeground(QColor("#FF9500"))
            else:
                rate_item.setForeground(QColor("#FF3B30"))
            self.table.setItem(i, 5, rate_item)

            self.table.setItem(i, 6, QTableWidgetItem(f"{r['coverage_statement']:.1f}%"))
            self.table.setItem(i, 7, QTableWidgetItem(f"{r['coverage_branch']:.1f}%"))
            self.table.setItem(i, 8, QTableWidgetItem(f"{r['coverage_mcdc']:.1f}%"))

        if should_close:
            conn.close()

    def _on_add(self):
        if not self.stage_id:
            return
        dlg = TestResultAddDialog(self.stage_id, self)
        if dlg.exec_() == QDialog.Accepted:
            self.load_stage(self.stage_id)
