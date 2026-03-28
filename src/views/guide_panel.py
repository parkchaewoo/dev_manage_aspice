"""ASPICE 가이드 패널 - 초보자용 한국어/영어 가이드"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QTextBrowser
)
from PyQt5.QtCore import Qt

from src.models.database import get_connection
from src.models.stage import StageModel
from src.utils.constants import SWE_STAGES


class GuidePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_lang = "ko"
        self.stage_id = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 언어 토글
        lang_layout = QHBoxLayout()
        self.btn_ko = QPushButton("한국어")
        self.btn_ko.setMaximumWidth(80)
        self.btn_ko.clicked.connect(lambda: self._set_lang("ko"))
        lang_layout.addWidget(self.btn_ko)

        self.btn_en = QPushButton("English")
        self.btn_en.setMaximumWidth(80)
        self.btn_en.setProperty("secondary", True)
        self.btn_en.clicked.connect(lambda: self._set_lang("en"))
        lang_layout.addWidget(self.btn_en)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)

        # 가이드 내용
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.setStyleSheet(
            "QTextBrowser { background-color: #FFFFFF; border: none; "
            "border-radius: 10px; padding: 12px; }"
        )
        layout.addWidget(self.browser)

        # 초기 내용
        self._show_welcome()

    def _set_lang(self, lang):
        self.current_lang = lang
        if lang == "ko":
            self.btn_ko.setProperty("secondary", False)
            self.btn_en.setProperty("secondary", True)
        else:
            self.btn_ko.setProperty("secondary", True)
            self.btn_en.setProperty("secondary", False)
        self.btn_ko.style().unpolish(self.btn_ko)
        self.btn_ko.style().polish(self.btn_ko)
        self.btn_en.style().unpolish(self.btn_en)
        self.btn_en.style().polish(self.btn_en)

        if self.stage_id:
            self.load_stage(self.stage_id)
        else:
            self._show_welcome()

    def _show_welcome(self):
        if self.current_lang == "ko":
            self.browser.setHtml("""
                <h2 style="color: #007AFF;">ASPICE 가이드</h2>
                <p>좌측 트리에서 SWE 단계를 선택하면 해당 단계에 대한 상세 가이드가 여기에 표시됩니다.</p>
                <h3>ASPICE V-Model이란?</h3>
                <p>Automotive SPICE는 자동차 소프트웨어 개발 프로세스의 품질을 평가하는 국제 표준입니다.</p>
                <p>V-Model은 개발(좌측)과 검증(우측)이 대칭을 이루는 개발 모델입니다:</p>
                <ul>
                    <li><b>SWE.1</b> 요구사항 분석 ↔ <b>SWE.6</b> 적격성 시험</li>
                    <li><b>SWE.2</b> 아키텍처 설계 ↔ <b>SWE.5</b> 통합 시험</li>
                    <li><b>SWE.3</b> 상세 설계/구현 ↔ <b>SWE.4</b> 단위 검증</li>
                </ul>
                <p style="color: #8E8E93;">각 단계를 클릭하면 무엇을, 왜 해야 하는지 안내해 드립니다.</p>
            """)
        else:
            self.browser.setHtml("""
                <h2 style="color: #007AFF;">ASPICE Guide</h2>
                <p>Select an SWE stage from the tree to see detailed guidance here.</p>
                <h3>What is ASPICE V-Model?</h3>
                <p>Automotive SPICE is an international standard for evaluating automotive software development process quality.</p>
                <p>The V-Model pairs development (left) with verification (right):</p>
                <ul>
                    <li><b>SWE.1</b> Requirements Analysis ↔ <b>SWE.6</b> Qualification Test</li>
                    <li><b>SWE.2</b> Architectural Design ↔ <b>SWE.5</b> Integration Test</li>
                    <li><b>SWE.3</b> Detailed Design ↔ <b>SWE.4</b> Unit Verification</li>
                </ul>
                <p style="color: #8E8E93;">Click on each stage to learn what to do and why.</p>
            """)

    def load_stage(self, stage_id):
        """단계별 가이드 표시"""
        self.stage_id = stage_id
        conn = get_connection()
        stage = StageModel.get_by_id(stage_id, conn)
        conn.close()

        if not stage:
            return

        swe = stage["swe_level"]

        try:
            from src.services.guide_service import STAGE_GUIDES
            guide = STAGE_GUIDES.get(swe, {}).get(self.current_lang, {})
        except ImportError:
            guide = {}

        if not guide:
            swe_info = SWE_STAGES.get(swe, {})
            lang_key = "name_ko" if self.current_lang == "ko" else "name_en"
            desc_key = "description_ko" if self.current_lang == "ko" else "description_en"
            self.browser.setHtml(
                f"<h2 style='color: #007AFF;'>{swe}: {swe_info.get(lang_key, swe)}</h2>"
                f"<p>{swe_info.get(desc_key, '')}</p>"
            )
            return

        # 가이드 HTML 생성
        docs_html = "".join(f"<li>{d}</li>" for d in guide.get("documents", []))
        tips_html = "".join(f"<li>{t}</li>" for t in guide.get("tips", []))

        pair_label = "V-Model 쌍" if self.current_lang == "ko" else "V-Model Pair"
        what_label = "무엇을 해야 하나요?" if self.current_lang == "ko" else "What to do?"
        why_label = "왜 중요한가요?" if self.current_lang == "ko" else "Why is it important?"
        docs_label = "필요한 문서" if self.current_lang == "ko" else "Required Documents"
        tips_label = "실무 팁" if self.current_lang == "ko" else "Practical Tips"
        next_label = "다음 단계" if self.current_lang == "ko" else "Next Step"

        self.browser.setHtml(f"""
            <h2 style="color: #007AFF;">{swe}: {guide.get('title', '')}</h2>

            <div style="background-color: #E8F0FE; padding: 10px; border-radius: 8px; margin: 8px 0;">
                <b>{pair_label}:</b> {guide.get('v_model_pair', '')}
            </div>

            <h3 style="color: #3A3A3C;">{what_label}</h3>
            <p>{guide.get('what', '')}</p>

            <h3 style="color: #3A3A3C;">{why_label}</h3>
            <p>{guide.get('why', '')}</p>

            <h3 style="color: #3A3A3C;">{docs_label}</h3>
            <ul>{docs_html}</ul>

            <h3 style="color: #3A3A3C;">{tips_label}</h3>
            <ul style="color: #FF9500;">{tips_html}</ul>

            <div style="background-color: #E8F5E9; padding: 10px; border-radius: 8px; margin-top: 12px;">
                <b>→ {next_label}:</b> {guide.get('next_step', '')}
            </div>
        """)
