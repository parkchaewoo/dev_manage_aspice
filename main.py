"""ASPICE Process Manager - 메인 진입점"""
import os
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from src.models.database import initialize_schema, is_db_initialized, get_connection
from src.services.demo_data_service import create_demo_data
from src.utils.styles import MAIN_STYLESHEET
from src.views.main_window import MainWindow


def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "VERSION")
    try:
        with open(version_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.1.0"


def main():
    # High DPI 지원
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("ASPICE Process Manager")
    version = get_version()
    app.setApplicationVersion(version)
    app.setStyleSheet(MAIN_STYLESHEET)

    # DB 초기화
    conn = get_connection()
    initialize_schema(conn)

    # 최초 실행 시 데모 데이터 생성
    if not is_db_initialized(conn):
        create_demo_data(conn)

    conn.close()

    # 메인 윈도우 표시
    window = MainWindow(version=version)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
