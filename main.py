"""ASPICE Process Manager - 메인 진입점"""
import os
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from src.models.database import initialize_schema, is_db_initialized, get_connection
from src.services.demo_data_service import create_demo_data
from src.utils.styles import MAIN_STYLESHEET, get_stylesheet, get_saved_theme
from src.views.main_window import MainWindow


def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "VERSION")
    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.4.2"


def _ensure_oem_phases(conn):
    """기존 OEM에 phases가 없으면 YAML 파일에서 자동 업데이트"""
    from src.models.oem import OemModel
    from src.utils.yaml_helpers import load_yaml_string, dump_yaml_string, load_yaml

    oems = OemModel.get_all(conn)
    base = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(base, "config", "default_oem_configs")

    # OEM 이름 → YAML 파일 매핑
    oem_file_map = {
        "HKMC": "hkmc.yaml",
        "Volkswagen": "volkswagen.yaml",
        "GM": "gm.yaml",
    }

    for oem in oems:
        config_yaml = oem["config_yaml"] or ""
        needs_update = False

        if config_yaml.strip():
            try:
                config = load_yaml_string(config_yaml)
                if config and isinstance(config, dict) and "phases" not in config:
                    needs_update = True
            except Exception:
                needs_update = True
        else:
            needs_update = True

        if needs_update:
            yaml_file = oem_file_map.get(oem["name"])
            if yaml_file:
                yaml_path = os.path.join(config_dir, yaml_file)
                if os.path.exists(yaml_path):
                    try:
                        new_config = load_yaml(yaml_path)
                        OemModel.update(oem["id"], config_yaml=dump_yaml_string(new_config), conn=conn)
                    except Exception:
                        pass


def main():
    # High DPI 지원
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("ASPICE Process Manager")
    version = get_version()
    app.setApplicationVersion(version)

    # 저장된 테마 적용
    theme = get_saved_theme()
    app.setStyleSheet(get_stylesheet(theme))

    # DB 초기화
    conn = get_connection()
    initialize_schema(conn)

    # 최초 실행 시 데모 데이터 생성
    if not is_db_initialized(conn):
        create_demo_data(conn)
    else:
        # 기존 DB의 OEM config에 phases 없으면 자동 업데이트
        _ensure_oem_phases(conn)

    conn.close()

    # 메인 윈도우 표시
    window = MainWindow(version=version)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
