"""iOS 캘린더 스타일 QSS 스타일시트"""

MAIN_STYLESHEET = """
/* === Global === */
QWidget {
    font-family: -apple-system, "Segoe UI", "Noto Sans KR", "Malgun Gothic", sans-serif;
    font-size: 14px;
    color: #1C1C1E;
    background-color: #F2F2F7;
}

/* === Main Window === */
QMainWindow {
    background-color: #F2F2F7;
}

QMainWindow::separator {
    width: 1px;
    background-color: #D1D1D6;
}

/* === Menu Bar === */
QMenuBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #D1D1D6;
    padding: 4px 8px;
    font-size: 13px;
}

QMenuBar::item {
    padding: 6px 12px;
    border-radius: 6px;
}

QMenuBar::item:selected {
    background-color: #E5E5EA;
}

QMenu {
    background-color: #FFFFFF;
    border: 1px solid #D1D1D6;
    border-radius: 12px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 6px;
}

QMenu::item:selected {
    background-color: #007AFF;
    color: white;
}

/* === Toolbar === */
QToolBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #D1D1D6;
    padding: 4px 8px;
    spacing: 8px;
}

QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    color: #007AFF;
}

QToolButton:hover {
    background-color: #E5E5EA;
}

QToolButton:pressed {
    background-color: #D1D1D6;
}

/* === Dock Widget (Side Panel) === */
QDockWidget {
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
    font-size: 13px;
}

QDockWidget::title {
    background-color: #FFFFFF;
    padding: 8px 12px;
    border-bottom: 1px solid #E5E5EA;
    font-weight: bold;
}

/* === Tree View === */
QTreeView {
    background-color: #FFFFFF;
    border: none;
    outline: none;
    font-size: 14px;
}

QTreeView::item {
    padding: 8px 12px;
    border-radius: 8px;
    margin: 1px 4px;
}

QTreeView::item:selected {
    background-color: #007AFF;
    color: white;
}

QTreeView::item:hover:!selected {
    background-color: #F2F2F7;
}

QTreeView::branch {
    background-color: #FFFFFF;
}

/* === Scroll Bar === */
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #C7C7CC;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #C7C7CC;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* === Push Button === */
QPushButton {
    background-color: #007AFF;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #0056CC;
}

QPushButton:pressed {
    background-color: #004099;
}

QPushButton:disabled {
    background-color: #C7C7CC;
    color: #8E8E93;
}

QPushButton[secondary="true"] {
    background-color: #E5E5EA;
    color: #007AFF;
}

QPushButton[secondary="true"]:hover {
    background-color: #D1D1D6;
}

QPushButton[danger="true"] {
    background-color: #FF3B30;
}

QPushButton[danger="true"]:hover {
    background-color: #CC2F26;
}

/* === Card Frame === */
QFrame[card="true"] {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: none;
    padding: 16px;
}

/* === Labels === */
QLabel {
    background-color: transparent;
}

QLabel[heading="true"] {
    font-size: 22px;
    font-weight: bold;
    color: #1C1C1E;
}

QLabel[subheading="true"] {
    font-size: 16px;
    font-weight: 600;
    color: #3A3A3C;
}

QLabel[caption="true"] {
    font-size: 12px;
    color: #8E8E93;
}

/* === Line Edit === */
QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #D1D1D6;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 14px;
}

QLineEdit:focus {
    border: 2px solid #007AFF;
}

/* === Text Edit === */
QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #D1D1D6;
    border-radius: 10px;
    padding: 10px;
    font-size: 14px;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #007AFF;
}

/* === Combo Box === */
QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #D1D1D6;
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 14px;
}

QComboBox:focus {
    border: 2px solid #007AFF;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #D1D1D6;
    border-radius: 10px;
    selection-background-color: #007AFF;
    selection-color: white;
}

/* === Tab Widget === */
QTabWidget::pane {
    border: none;
    background-color: #FFFFFF;
    border-radius: 12px;
}

QTabBar::tab {
    background-color: transparent;
    padding: 10px 20px;
    font-size: 14px;
    color: #8E8E93;
    border-bottom: 2px solid transparent;
}

QTabBar::tab:selected {
    color: #007AFF;
    border-bottom: 2px solid #007AFF;
}

QTabBar::tab:hover:!selected {
    color: #3A3A3C;
}

/* === Table Widget === */
QTableWidget, QTableView {
    background-color: #FFFFFF;
    border: none;
    border-radius: 12px;
    gridline-color: #E5E5EA;
    font-size: 13px;
}

QTableWidget::item, QTableView::item {
    padding: 8px 12px;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #007AFF;
    color: white;
}

QHeaderView::section {
    background-color: #F2F2F7;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #D1D1D6;
    font-weight: 600;
    font-size: 12px;
    color: #8E8E93;
    text-transform: uppercase;
}

/* === Check Box === */
QCheckBox {
    spacing: 8px;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    border: 2px solid #D1D1D6;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #007AFF;
    border: 2px solid #007AFF;
}

/* === Progress Bar === */
QProgressBar {
    background-color: #E5E5EA;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    font-size: 11px;
}

QProgressBar::chunk {
    background-color: #007AFF;
    border-radius: 4px;
}

/* === Dialog === */
QDialog {
    background-color: #F2F2F7;
}

/* === Group Box === */
QGroupBox {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: none;
    padding: 16px;
    padding-top: 32px;
    margin-top: 8px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: #8E8E93;
    font-size: 12px;
    text-transform: uppercase;
}

/* === Status Bar === */
QStatusBar {
    background-color: #FFFFFF;
    border-top: 1px solid #D1D1D6;
    font-size: 12px;
    color: #8E8E93;
    padding: 4px 12px;
}

/* === Splitter === */
QSplitter::handle {
    background-color: #D1D1D6;
    width: 1px;
}

/* === Tool Tip === */
QToolTip {
    background-color: #1C1C1E;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
}
"""
