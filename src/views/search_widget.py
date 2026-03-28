"""Search widget for documents and checklist items / 검색 위젯"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from src.models.database import get_connection


def search_all(keyword, conn=None):
    """Search documents and checklist items by keyword.

    Returns list of dicts with type, id, name, context.
    """
    if not keyword or not keyword.strip():
        return []

    should_close = conn is None
    if conn is None:
        conn = get_connection()

    results = []
    like = f"%{keyword.strip()}%"

    # Search documents by name
    doc_rows = conn.execute(
        """SELECT d.id, d.name, d.status, s.swe_level, p.name as project_name
           FROM documents d
           JOIN stages s ON d.stage_id = s.id
           JOIN projects p ON s.project_id = p.id
           WHERE d.name LIKE ?
           ORDER BY d.name
           LIMIT 50""",
        (like,),
    ).fetchall()

    for row in doc_rows:
        results.append({
            "type": "document",
            "id": row["id"],
            "name": row["name"],
            "context": f"{row['project_name']} > {row['swe_level']} [{row['status']}]",
        })

    # Search checklist items by description
    cl_rows = conn.execute(
        """SELECT ci.id, ci.description, ci.is_checked, s.swe_level, p.name as project_name
           FROM checklist_items ci
           JOIN stages s ON ci.stage_id = s.id
           JOIN projects p ON s.project_id = p.id
           WHERE ci.description LIKE ?
           ORDER BY ci.description
           LIMIT 50""",
        (like,),
    ).fetchall()

    for row in cl_rows:
        checked = "Done" if row["is_checked"] else "Pending"
        results.append({
            "type": "checklist",
            "id": row["id"],
            "name": row["description"],
            "context": f"{row['project_name']} > {row['swe_level']} [{checked}]",
        })

    if should_close:
        conn.close()

    return results


class SearchWidget(QWidget):
    """Search panel with text input and results list."""

    # Emitted when a result is selected: (type, id)
    result_selected = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)
        self.setMinimumWidth(450)
        self.setMaximumHeight(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search documents & checklists / 검색...")
        self.search_input.setClearButtonEnabled(True)
        layout.addWidget(self.search_input)

        # Results count label
        self.count_label = QLabel("")
        self.count_label.setProperty("caption", True)
        layout.addWidget(self.count_label)

        # Results list
        self.results_list = QListWidget()
        self.results_list.setAlternatingRowColors(True)
        layout.addWidget(self.results_list)

        # Debounce timer for search
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(300)
        self._timer.timeout.connect(self._do_search)

        self.search_input.textChanged.connect(self._on_text_changed)
        self.results_list.itemClicked.connect(self._on_item_clicked)

    def _on_text_changed(self, text):
        self._timer.start()

    def _do_search(self):
        keyword = self.search_input.text().strip()
        self.results_list.clear()

        if not keyword:
            self.count_label.setText("")
            return

        results = search_all(keyword)
        self.count_label.setText(f"{len(results)} result(s) found")

        for r in results:
            icon = "\U0001F4C4" if r["type"] == "document" else "\u2611"
            text = f"{icon}  {r['name']}\n     {r['context']}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, (r["type"], r["id"]))
            self.results_list.addItem(item)

    def _on_item_clicked(self, item):
        data = item.data(Qt.UserRole)
        if data:
            result_type, result_id = data
            self.result_selected.emit(result_type, result_id)
            self.hide()

    def show_at(self, global_pos):
        """Show the search popup at a specific position."""
        self.move(global_pos)
        self.show()
        self.search_input.setFocus()
        self.search_input.selectAll()
