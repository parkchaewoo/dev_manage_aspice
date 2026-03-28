"""문서 편집기 / 목록 위젯 - 미리보기 + 편집 분리"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QPushButton, QComboBox,
    QHeaderView, QTextBrowser, QTextEdit, QDialog, QLineEdit, QFormLayout,
    QFileDialog, QMessageBox, QGroupBox, QTabWidget, QSplitter, QSlider
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

import os
import re
from datetime import date

from src.models.document import DocumentModel
from src.models.database import get_connection
from src.utils.constants import DocumentStatus, STATUS_COLORS
from src.utils.styles import get_user_name


def _md_to_html(md_text):
    """마크다운 → HTML 변환 (간단 버전, 가이드 코멘트 강조)"""
    lines = md_text.split("\n")
    html_lines = []
    in_table = False
    in_code = False

    for line in lines:
        stripped = line.strip()

        # 코드 블록
        if stripped.startswith("```"):
            if in_code:
                html_lines.append("</pre>")
                in_code = False
            else:
                html_lines.append("<pre style='background:#F2F2F7;padding:12px;border-radius:8px;font-size:12px;overflow-x:auto;'>")
                in_code = True
            continue
        if in_code:
            html_lines.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue

        # GUIDE 코멘트 → 파란 가이드 박스로 변환
        guide_match = re.match(r'<!--\s*GUIDE:\s*(.+?)\s*-->', stripped)
        if guide_match:
            guide_text = guide_match.group(1)
            html_lines.append(
                f'<div style="background:#E8F0FE;border-left:4px solid #007AFF;'
                f'padding:8px 12px;margin:8px 0;border-radius:4px;font-size:13px;color:#007AFF;">'
                f'💡 <b>Guide:</b> {guide_text}</div>'
            )
            continue

        # 헤딩
        if stripped.startswith("######"):
            html_lines.append(f"<h6 style='color:#3A3A3C;margin:12px 0 4px;'>{stripped[6:].strip()}</h6>")
        elif stripped.startswith("#####"):
            html_lines.append(f"<h5 style='color:#3A3A3C;margin:12px 0 4px;'>{stripped[5:].strip()}</h5>")
        elif stripped.startswith("####"):
            html_lines.append(f"<h4 style='color:#3A3A3C;margin:14px 0 6px;'>{stripped[4:].strip()}</h4>")
        elif stripped.startswith("###"):
            html_lines.append(f"<h3 style='color:#1C1C1E;margin:16px 0 6px;'>{stripped[3:].strip()}</h3>")
        elif stripped.startswith("##"):
            html_lines.append(f"<h2 style='color:#007AFF;margin:20px 0 8px;border-bottom:1px solid #E5E5EA;padding-bottom:6px;'>{stripped[2:].strip()}</h2>")
        elif stripped.startswith("# "):
            html_lines.append(f"<h1 style='color:#007AFF;margin:0 0 12px;'>{stripped[1:].strip()}</h1>")
        elif stripped.startswith("---"):
            html_lines.append("<hr style='border:none;border-top:1px solid #E5E5EA;margin:16px 0;'>")
        elif stripped.startswith("| "):
            # 테이블
            if not in_table:
                html_lines.append("<table style='border-collapse:collapse;width:100%;margin:8px 0;font-size:13px;'>")
                in_table = True
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if all(set(c) <= {"-", ":", " "} for c in cells):
                continue
            row_html = "<tr>" + "".join(
                f"<td style='border:1px solid #D1D1D6;padding:6px 10px;'>{c}</td>" for c in cells
            ) + "</tr>"
            html_lines.append(row_html)
        elif stripped.startswith("- "):
            html_lines.append(f"<li style='margin:2px 0;'>{stripped[2:]}</li>")
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False
            if stripped:
                # Bold
                processed = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', stripped)
                # Inline code
                processed = re.sub(r'`(.+?)`', r'<code style="background:#F2F2F7;padding:2px 4px;border-radius:3px;font-size:12px;">\1</code>', processed)
                html_lines.append(f"<p style='margin:4px 0;line-height:1.6;'>{processed}</p>")

    if in_table:
        html_lines.append("</table>")
    if in_code:
        html_lines.append("</pre>")

    return "\n".join(html_lines)


class DocumentEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stage_id = None
        self._selected_doc_id = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 좌우 분할: 좌=문서 목록, 우=에디터
        splitter = QSplitter(Qt.Horizontal)

        # ===== 좌측: 문서 목록 패널 =====
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 4, 0)
        left_layout.setSpacing(6)

        left_header = QHBoxLayout()
        title_lbl = QLabel("Documents")
        title_lbl.setStyleSheet("font-weight:bold;")
        left_header.addWidget(title_lbl)
        left_header.addStretch()
        left_layout.addLayout(left_header)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Document", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self._on_cell_clicked)
        left_layout.addWidget(self.table)

        splitter.addWidget(left_panel)

        # ===== 우측: 에디터 패널 =====
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 0, 0, 0)
        right_layout.setSpacing(6)

        # 문서 제목 + 내보내기 버튼
        title_row = QHBoxLayout()
        self.doc_title = QLabel("Select a document")
        self.doc_title.setStyleSheet("font-size:15px; font-weight:bold; color:#007AFF;")
        title_row.addWidget(self.doc_title)
        title_row.addStretch()

        self.btn_export_md = QPushButton("Export MD")
        self.btn_export_md.setProperty("secondary", True)
        self.btn_export_md.setMaximumWidth(110)
        self.btn_export_md.clicked.connect(lambda: self._export_md(self._selected_doc_id) if self._selected_doc_id else None)
        title_row.addWidget(self.btn_export_md)

        self.btn_export_html = QPushButton("Export HTML")
        self.btn_export_html.setProperty("secondary", True)
        self.btn_export_html.setMaximumWidth(120)
        self.btn_export_html.clicked.connect(lambda: self._export_html(self._selected_doc_id) if self._selected_doc_id else None)
        title_row.addWidget(self.btn_export_html)

        # 글자 크기 조절
        title_row.addWidget(QLabel("A"))
        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setMinimum(10)
        self.font_slider.setMaximum(20)
        self.font_slider.setValue(13)
        self.font_slider.setMaximumWidth(80)
        self.font_slider.setToolTip("Font size / 글자 크기")
        self.font_slider.valueChanged.connect(self._on_font_size_changed)
        title_row.addWidget(self.font_slider)
        self.font_size_label = QLabel("13")
        self.font_size_label.setMaximumWidth(20)
        title_row.addWidget(self.font_size_label)

        right_layout.addLayout(title_row)

        # 미리보기 / 편집 탭
        self.editor_tabs = QTabWidget()

        # 탭 1: 미리보기
        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(False)
        self.preview.setStyleSheet(
            "QTextBrowser { background:#FFFFFF; border:1px solid #E5E5EA; "
            "border-radius:8px; padding:12px; }"
        )
        self.editor_tabs.addTab(self.preview, "Preview")

        # 탭 2: Form Editor (테이블 GUI 편집)
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(4)

        form_help = QLabel("Click cells to edit directly / 셀을 클릭하여 직접 편집하세요")
        form_help.setStyleSheet("color:#8E8E93; font-size:11px; padding:2px;")
        form_layout.addWidget(form_help)

        # 스크롤 가능한 폼 영역
        from PyQt5.QtWidgets import QScrollArea
        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setFrameShape(QFrame.NoFrame)
        self.form_container = QWidget()
        self.form_inner_layout = QVBoxLayout(self.form_container)
        self.form_inner_layout.setSpacing(12)
        self.form_inner_layout.addStretch()
        form_scroll.setWidget(self.form_container)
        form_layout.addWidget(form_scroll)

        form_btn_row = QHBoxLayout()
        form_btn_row.addStretch()
        btn_save_form = QPushButton("Save Content")
        btn_save_form.setMaximumWidth(140)
        btn_save_form.clicked.connect(self._save_form_to_content)
        form_btn_row.addWidget(btn_save_form)
        form_layout.addLayout(form_btn_row)

        self.editor_tabs.addTab(form_widget, "Form Edit")

        # 탭 3: Source (마크다운 원본)
        source_widget = QWidget()
        source_layout = QVBoxLayout(source_widget)
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.setSpacing(4)

        self.content_edit = QTextEdit()
        self.content_edit.setStyleSheet(
            "QTextEdit { font-family:'Courier New','Monaco','Menlo',monospace; "
            "font-size:13px; background:#FAFAFA; "
            "border:1px solid #E5E5EA; border-radius:8px; padding:8px; }"
        )
        self.content_edit.setPlaceholderText("Markdown source")
        source_layout.addWidget(self.content_edit)

        src_btn_row = QHBoxLayout()
        src_btn_row.addStretch()
        btn_refresh = QPushButton("Refresh Preview")
        btn_refresh.setProperty("secondary", True)
        btn_refresh.setMaximumWidth(160)
        btn_refresh.clicked.connect(self._refresh_preview)
        src_btn_row.addWidget(btn_refresh)
        btn_save_src = QPushButton("Save Content")
        btn_save_src.setMaximumWidth(140)
        btn_save_src.clicked.connect(self._save_content)
        src_btn_row.addWidget(btn_save_src)
        source_layout.addLayout(src_btn_row)

        self.editor_tabs.addTab(source_widget, "Source")
        right_layout.addWidget(self.editor_tabs, 1)

        # 버전 이력 (접기)
        self.version_group = QGroupBox("Version History")
        self.version_group.setCheckable(True)
        self.version_group.setChecked(False)
        version_layout = QVBoxLayout(self.version_group)
        self.version_table = QTableWidget()
        self.version_table.setColumnCount(4)
        self.version_table.setHorizontalHeaderLabels(["Ver", "Date", "By", "Description"])
        self.version_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.version_table.verticalHeader().setVisible(False)
        self.version_table.setMaximumHeight(100)
        version_layout.addWidget(self.version_table)
        self.version_group.toggled.connect(self._on_version_group_toggled)
        right_layout.addWidget(self.version_group)

        splitter.addWidget(right_panel)
        splitter.setSizes([280, 520])

        layout.addWidget(splitter)

    def load_stage(self, stage_id, conn=None):
        """단계의 문서 목록 로드"""
        self.stage_id = stage_id
        should_close = conn is None
        if conn is None:
            conn = get_connection()

        docs = DocumentModel.get_by_stage(stage_id, conn)
        self.table.setRowCount(len(docs))

        for i, doc in enumerate(docs):
            name_item = QTableWidgetItem(doc["name"])
            name_item.setData(Qt.UserRole, doc["id"])
            self.table.setItem(i, 0, name_item)

            status = doc["status"]
            status_item = QTableWidgetItem(status)
            color = STATUS_COLORS.get(status, "#8E8E93")
            status_item.setForeground(QColor("white"))
            status_item.setBackground(QColor(color))
            self.table.setItem(i, 1, status_item)

        # 첫 문서 자동 선택
        if len(docs) > 0:
            self.table.selectRow(0)
            self._on_cell_clicked(0, 0)

        if should_close:
            conn.close()

    def _on_cell_clicked(self, row, col):
        """문서 선택 → 미리보기 + 편집기 로드"""
        item = self.table.item(row, 0)
        if not item:
            return
        doc_id = item.data(Qt.UserRole)
        doc = DocumentModel.get_by_id(doc_id)
        if not doc:
            return

        self._selected_doc_id = doc_id
        self.doc_title.setText(f"📄 {doc['name']}  [{doc['status']}]")

        # 콘텐츠 로드
        try:
            content = doc["content"] or ""
        except (IndexError, KeyError):
            content = ""

        # Source 편집기에 마크다운 원본
        self.content_edit.setPlainText(content)

        # Form Editor 채우기
        self._build_form_from_content(content)

        # 미리보기에 렌더링된 HTML
        if content.strip():
            html = _md_to_html(content)
            self.preview.setHtml(
                f"<div style='font-family:\"Helvetica Neue\",sans-serif;'>{html}</div>"
            )
        else:
            self.preview.setHtml(
                "<div style='text-align:center;padding:40px;color:#8E8E93;'>"
                "<h2>No Content</h2>"
                "<p>Switch to <b>Form Edit</b> to start writing.</p>"
                "</div>"
            )

        # 미리보기 탭으로 전환
        self.editor_tabs.setCurrentIndex(0)

        # 버전 이력 로드
        self._load_version_history(doc_id)

    def _build_form_from_content(self, content):
        """마크다운 내용을 파싱하여 GUI 폼 위젯으로 변환"""
        # 기존 폼 위젯 제거
        while self.form_inner_layout.count() > 1:
            item = self.form_inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._form_sections = []  # (type, widget, section_title) 저장

        if not content.strip():
            lbl = QLabel("No content. Create from Form Edit or Source tab.")
            lbl.setStyleSheet("color:#8E8E93; padding:20px;")
            self.form_inner_layout.insertWidget(0, lbl)
            return

        lines = content.split("\n")
        i = 0
        section_idx = 0
        while i < len(lines):
            line = lines[i].strip()

            # 섹션 제목 (## 또는 #)
            if line.startswith("## ") or line.startswith("# "):
                title = line.lstrip("#").strip()
                title_label = QLabel(title)
                title_label.setStyleSheet(
                    "font-size:14px; font-weight:bold; color:#007AFF; "
                    "padding:8px 0 2px; border-bottom:1px solid #E5E5EA;"
                )
                self.form_inner_layout.insertWidget(section_idx, title_label)
                self._form_sections.append(("heading", title_label, title))
                section_idx += 1
                i += 1
                continue

            # 설명 텍스트 (괄호로 시작)
            if line.startswith("(") and line.endswith(")"):
                desc = QLabel(line)
                desc.setStyleSheet("color:#8E8E93; font-size:12px; padding:2px 0;")
                desc.setWordWrap(True)
                self.form_inner_layout.insertWidget(section_idx, desc)
                self._form_sections.append(("desc", desc, line))
                section_idx += 1
                i += 1
                continue

            # 테이블 → QTableWidget
            if line.startswith("|"):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    table_lines.append(lines[i].strip())
                    i += 1

                # 구분선 제거, 셀 파싱
                data_rows = []
                for tl in table_lines:
                    cells = [c.strip() for c in tl.split("|")[1:-1]]
                    if cells and not all(set(c) <= {"-", ":", " "} for c in cells):
                        data_rows.append(cells)

                if len(data_rows) >= 1:
                    headers = data_rows[0]
                    body = data_rows[1:] if len(data_rows) > 1 else []

                    tw = QTableWidget()
                    tw.setColumnCount(len(headers))
                    tw.setHorizontalHeaderLabels(headers)
                    tw.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                    tw.verticalHeader().setVisible(False)
                    tw.setRowCount(max(len(body), 3))  # 최소 3행

                    for r, row_cells in enumerate(body):
                        for c, cell in enumerate(row_cells):
                            if c < len(headers):
                                tw.setItem(r, c, QTableWidgetItem(cell))

                    # 빈 행 채우기
                    for r in range(len(body), tw.rowCount()):
                        for c in range(len(headers)):
                            tw.setItem(r, c, QTableWidgetItem(""))

                    row_height = 30
                    tw.setMinimumHeight(min(row_height * (tw.rowCount() + 1) + 10, 250))
                    tw.setMaximumHeight(300)

                    self.form_inner_layout.insertWidget(section_idx, tw)
                    self._form_sections.append(("table", tw, headers))
                    section_idx += 1
                continue

            # 코드 블록
            if line.startswith("```"):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # skip closing ```

                code_edit = QTextEdit()
                code_edit.setPlainText("\n".join(code_lines))
                code_edit.setStyleSheet(
                    "QTextEdit { font-family:monospace; font-size:12px; "
                    "background:#F2F2F7; border:1px solid #D1D1D6; border-radius:6px; padding:6px; }"
                )
                code_edit.setMaximumHeight(150)
                self.form_inner_layout.insertWidget(section_idx, code_edit)
                self._form_sections.append(("code", code_edit, ""))
                section_idx += 1
                continue

            # 일반 텍스트 (빈 줄, ---, 기타 스킵)
            if line and line != "---" and not line.startswith("<!--"):
                text_edit = QLineEdit()
                text_edit.setText(line)
                text_edit.setStyleSheet("padding:4px;")
                self.form_inner_layout.insertWidget(section_idx, text_edit)
                self._form_sections.append(("text", text_edit, ""))
                section_idx += 1

            i += 1

    def _save_form_to_content(self):
        """Form Editor의 내용을 마크다운으로 변환하여 저장"""
        if not self._selected_doc_id:
            QMessageBox.warning(self, "Warning", "No document selected.")
            return

        lines = []
        for stype, widget, meta in self._form_sections:
            if stype == "heading":
                depth = "##" if not meta.startswith("#") else "#"
                lines.append(f"\n{depth} {meta}\n")
            elif stype == "desc":
                lines.append(meta)
                lines.append("")
            elif stype == "table":
                headers = meta
                lines.append("| " + " | ".join(headers) + " |")
                lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                for r in range(widget.rowCount()):
                    cells = []
                    for c in range(widget.columnCount()):
                        item = widget.item(r, c)
                        cells.append(item.text() if item else "")
                    if any(c.strip() for c in cells):  # 빈 행 스킵
                        lines.append("| " + " | ".join(cells) + " |")
                lines.append("")
            elif stype == "code":
                lines.append("```")
                lines.append(widget.toPlainText())
                lines.append("```")
                lines.append("")
            elif stype == "text":
                lines.append(widget.text())
                lines.append("")

        new_content = "\n".join(lines)

        # Source 편집기와 동기화
        self.content_edit.setPlainText(new_content)

        # DB에 저장
        self._save_content()

    def _on_font_size_changed(self, size):
        """글자 크기 변경"""
        self.font_size_label.setText(str(size))
        self.content_edit.setStyleSheet(
            f"QTextEdit {{ font-family:'Courier New','Monaco','Menlo',monospace; "
            f"font-size:{size}px; background:#FAFAFA; "
            f"border:1px solid #E5E5EA; border-radius:8px; padding:8px; }}"
        )
        self.preview.setStyleSheet(
            f"QTextBrowser {{ background:#FFFFFF; border:1px solid #E5E5EA; "
            f"border-radius:8px; padding:12px; font-size:{size}px; }}"
        )

    def _refresh_preview(self):
        """편집 내용으로 미리보기 새로고침"""
        content = self.content_edit.toPlainText()
        if content.strip():
            html = _md_to_html(content)
            self.preview.setHtml(
                f"<div style='font-family:\"Helvetica Neue\",sans-serif;'>{html}</div>"
            )
            self.editor_tabs.setCurrentIndex(0)
        else:
            self.preview.setHtml(
                "<div style='text-align:center;padding:40px;color:#8E8E93;'>"
                "<p>No content to preview / 미리볼 내용이 없습니다</p></div>"
            )

    def _save_content(self):
        """문서 내용 저장 (버전 스냅샷 포함)"""
        if not self._selected_doc_id:
            QMessageBox.warning(self, "Warning", "No document selected.\n문서를 먼저 선택하세요.")
            return

        new_content = self.content_edit.toPlainText()
        conn = get_connection()
        try:
            # 이전 내용 스냅샷 저장
            old_doc = DocumentModel.get_by_id(self._selected_doc_id, conn)
            if old_doc:
                try:
                    old_content = old_doc["content"] or ""
                except (IndexError, KeyError):
                    old_content = ""
                if old_content:
                    ver_count = conn.execute(
                        "SELECT COUNT(*) FROM document_versions WHERE document_id = ?",
                        (self._selected_doc_id,)
                    ).fetchone()[0]
                    user = get_user_name() or "System"
                    conn.execute(
                        "INSERT INTO document_versions (document_id, version_number, content_snapshot, change_description, changed_by) VALUES (?,?,?,?,?)",
                        (self._selected_doc_id, ver_count + 1, old_content, "Content updated", user)
                    )
                    conn.commit()

            # 새 내용 저장
            DocumentModel.update(self._selected_doc_id, content=new_content, conn=conn)
            conn.close()

            # 미리보기 새로고침
            self._refresh_preview()
            self._load_version_history(self._selected_doc_id)
            QMessageBox.information(self, "Saved", "Content saved successfully.\n내용이 저장되었습니다.")
        except Exception as e:
            conn.close()
            QMessageBox.warning(self, "Error", f"Failed to save:\n{e}")

    def _load_version_history(self, doc_id):
        """버전 이력 로드"""
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM document_versions WHERE document_id = ? ORDER BY version_number DESC",
                (doc_id,)
            ).fetchall()
        except Exception:
            rows = []
        conn.close()

        self.version_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.version_table.setItem(i, 0, QTableWidgetItem(str(row["version_number"])))
            self.version_table.setItem(i, 1, QTableWidgetItem(str(row["created_at"] or "")))
            self.version_table.setItem(i, 2, QTableWidgetItem(str(row["changed_by"] or "")))
            self.version_table.setItem(i, 3, QTableWidgetItem(str(row["change_description"] or "")))

    def _on_version_group_toggled(self, checked):
        self.version_table.setVisible(checked)

    def _load_template_content(self, template_type):
        """Load template content for auto-fill."""
        from src.services.export_service import _TEMPLATE_MAP, _TEMPLATES_DIR
        from src.models.stage import StageModel
        from src.models.project import ProjectModel
        from src.models.oem import OemModel

        filename = _TEMPLATE_MAP.get(template_type)
        if not filename and self.stage_id:
            stage = StageModel.get_by_id(self.stage_id)
            if stage:
                filename = _TEMPLATE_MAP.get(stage["swe_level"])
        if not filename:
            return ""
        path = os.path.join(_TEMPLATES_DIR, filename)
        if not os.path.isfile(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        project_name, oem_name = "", ""
        if self.stage_id:
            stage = StageModel.get_by_id(self.stage_id)
            if stage:
                project = ProjectModel.get_by_id(stage["project_id"])
                if project:
                    project_name = project["name"]
                    oem = OemModel.get_by_id(project["oem_id"])
                    if oem:
                        oem_name = oem["name"]

        content = content.replace("{project_name}", project_name)
        content = content.replace("{oem_name}", oem_name)
        content = content.replace("{date}", str(date.today()))
        return content

    def _add_document(self):
        if not self.stage_id:
            return
        dialog = DocumentDialog(self, stage_id=self.stage_id)
        if dialog.exec_():
            data = dialog.get_data()
            try:
                template_type = data.get("template_type", "")
                template_content = self._load_template_content(template_type)
                if template_content:
                    data["content"] = template_content
                DocumentModel.create(self.stage_id, **data)
                self.load_stage(self.stage_id)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to create document:\n{e}")

    def _edit_document(self, doc_id):
        doc = DocumentModel.get_by_id(doc_id)
        if not doc:
            return
        dialog = DocumentDialog(self, doc)
        if dialog.exec_():
            data = dialog.get_data()
            DocumentModel.update(doc_id, **data)
            self.load_stage(self.stage_id)

    def _export_md(self, doc_id):
        from src.services.export_service import export_to_markdown
        path, _ = QFileDialog.getSaveFileName(self, "Export as Markdown", "", "Markdown (*.md)")
        if path:
            try:
                export_to_markdown(doc_id, path)
                QMessageBox.information(self, "Export", f"Exported to:\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))

    def _export_html(self, doc_id):
        from src.services.export_service import export_to_html
        path, _ = QFileDialog.getSaveFileName(self, "Export as HTML", "", "HTML (*.html)")
        if path:
            try:
                export_to_html(doc_id, path)
                QMessageBox.information(self, "Export", f"Exported to:\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))


class DocumentDialog(QDialog):
    def __init__(self, parent=None, doc=None, stage_id=None):
        super().__init__(parent)
        self.setWindowTitle("Document / 문서" if not doc else "Edit Document / 문서 편집")
        self.setMinimumWidth(400)
        self.doc = doc
        self.stage_id = stage_id
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Document name / 문서명")
        layout.addRow("Name / 이름:", self.name_edit)

        self.template_edit = QLineEdit()
        self.template_edit.setPlaceholderText("e.g., srs, sad, sdd, ut_plan, qt_report")
        layout.addRow("Template ID:", self.template_edit)

        self.status_combo = QComboBox()
        self.status_combo.addItems(DocumentStatus.ALL)
        layout.addRow("Status / 상태:", self.status_combo)

        self.reviewer_edit = QLineEdit()
        layout.addRow("Reviewer / 검토자:", self.reviewer_edit)

        self.notes_edit = QLineEdit()
        layout.addRow("Notes / 메모:", self.notes_edit)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save / 저장")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel / 취소")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)

        if self.doc:
            self.name_edit.setText(self.doc["name"])
            self.template_edit.setText(self.doc["template_type"] or "")
            idx = self.status_combo.findText(self.doc["status"])
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)
            self.reviewer_edit.setText(self.doc["reviewer"] or "")
            self.notes_edit.setText(self.doc["notes"] or "")
        elif self.stage_id:
            try:
                auto_id = DocumentModel.get_next_id(self.stage_id)
                self.name_edit.setText(auto_id)
            except Exception:
                pass

    def get_data(self):
        return {
            "name": self.name_edit.text(),
            "template_type": self.template_edit.text(),
            "status": self.status_combo.currentText(),
            "reviewer": self.reviewer_edit.text(),
            "notes": self.notes_edit.text(),
        }
