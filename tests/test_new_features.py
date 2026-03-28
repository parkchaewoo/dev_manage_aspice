"""v0.2.0 신규 기능 테스트"""
import os
import sys
import json
import sqlite3
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import get_connection, initialize_schema
from src.models.oem import OemModel
from src.models.project import ProjectModel
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.checklist import ChecklistModel
from src.models.schedule import ScheduleModel


class TestDocumentAutoId(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        initialize_schema(self.conn)
        self.oem_id = OemModel.create("OEM", conn=self.conn)
        self.proj_id = ProjectModel.create(self.oem_id, "Proj", conn=self.conn)
        self.stage_id = StageModel.create(self.proj_id, "SWE.1", conn=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_auto_id_generation(self):
        """자동 ID 채번 테스트"""
        next_id = DocumentModel.get_next_id(self.stage_id, "REQ", self.conn)
        self.assertEqual(next_id, "SWE1-REQ-001")

        DocumentModel.create(self.stage_id, "SWE1-REQ-001", conn=self.conn)
        next_id = DocumentModel.get_next_id(self.stage_id, "REQ", self.conn)
        self.assertEqual(next_id, "SWE1-REQ-002")

    def test_auto_id_different_stages(self):
        """다른 단계는 별도 번호 체계"""
        stage2 = StageModel.create(self.proj_id, "SWE.2", conn=self.conn)
        DocumentModel.create(self.stage_id, "Doc1", conn=self.conn)
        DocumentModel.create(self.stage_id, "Doc2", conn=self.conn)

        next1 = DocumentModel.get_next_id(self.stage_id, "REQ", self.conn)
        next2 = DocumentModel.get_next_id(stage2, "SAD", self.conn)
        self.assertEqual(next1, "SWE1-REQ-003")
        self.assertEqual(next2, "SWE2-SAD-001")


class TestExportService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        initialize_schema(self.conn)
        self.oem_id = OemModel.create("TestOEM", conn=self.conn)
        self.proj_id = ProjectModel.create(self.oem_id, "TestProject", conn=self.conn)
        self.stage_id = StageModel.create(self.proj_id, "SWE.1", conn=self.conn)
        self.doc_id = DocumentModel.create(self.stage_id, "SRS", template_type="srs", conn=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_export_to_markdown(self):
        """마크다운 내보내기 테스트"""
        from src.services.export_service import export_to_markdown
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            path = f.name
        try:
            export_to_markdown(self.doc_id, path, self.conn)
            self.assertTrue(os.path.exists(path))
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn("TestProject", content)
        finally:
            os.unlink(path)

    def test_export_project_report(self):
        """프로젝트 보고서 내보내기 테스트"""
        from src.services.export_service import export_project_report
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            path = f.name
        try:
            export_project_report(self.proj_id, path, self.conn)
            self.assertTrue(os.path.exists(path))
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn("TestProject", content)
            self.assertIn("SWE.1", content)
        finally:
            os.unlink(path)


class TestSearchFunction(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        initialize_schema(self.conn)
        oem = OemModel.create("OEM", conn=self.conn)
        proj = ProjectModel.create(oem, "MyProject", conn=self.conn)
        stage = StageModel.create(proj, "SWE.1", conn=self.conn)
        DocumentModel.create(stage, "Steering Requirements Spec", conn=self.conn)
        DocumentModel.create(stage, "Brake Safety Analysis", conn=self.conn)
        ChecklistModel.create(stage, "Requirements have unique IDs", self.conn)

    def tearDown(self):
        self.conn.close()

    def test_search_documents(self):
        """문서 검색 테스트"""
        from src.models.database import search_all
        results = search_all("Steering", self.conn)
        self.assertGreaterEqual(len(results), 1)
        self.assertTrue(any("Steering" in r["name"] for r in results))

    def test_search_checklist(self):
        """체크리스트 검색 테스트"""
        from src.models.database import search_all
        results = search_all("unique IDs", self.conn)
        self.assertGreaterEqual(len(results), 1)

    def test_search_no_results(self):
        """검색 결과 없음 테스트"""
        from src.models.database import search_all
        results = search_all("xyznonexistent", self.conn)
        self.assertEqual(len(results), 0)


class TestBackupService(unittest.TestCase):
    def test_export_import_json(self):
        """JSON 내보내기/가져오기 테스트"""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        initialize_schema(conn)
        OemModel.create("TestOEM", description="Test", conn=conn)

        from src.services.backup_service import export_to_json, import_from_json
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            export_to_json(path, conn)
            self.assertTrue(os.path.exists(path))

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.assertIn("oems", data)
            self.assertEqual(len(data["oems"]), 1)

            # 새 DB에 가져오기
            conn2 = sqlite3.connect(":memory:")
            conn2.row_factory = sqlite3.Row
            conn2.execute("PRAGMA foreign_keys = ON")
            initialize_schema(conn2)
            import_from_json(path, conn2)
            oems = OemModel.get_all(conn2)
            self.assertEqual(len(oems), 1)
            conn2.close()
        finally:
            os.unlink(path)
        conn.close()


class TestNotificationService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        initialize_schema(self.conn)
        oem = OemModel.create("OEM", conn=self.conn)
        self.proj = ProjectModel.create(oem, "Proj", conn=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_overdue_detection(self):
        """지연 마일스톤 감지"""
        ScheduleModel.create(self.proj, "Past milestone", "2020-01-01", conn=self.conn)
        ScheduleModel.create(self.proj, "Future milestone", "2030-01-01", conn=self.conn)

        from src.services.notification_service import check_overdue_milestones
        overdue = check_overdue_milestones(self.conn)
        self.assertGreaterEqual(len(overdue), 1)
        self.assertTrue(any("Past" in m["name"] for m in overdue))

    def test_upcoming_detection(self):
        """임박한 마일스톤 감지"""
        from datetime import date, timedelta
        soon = (date.today() + timedelta(days=3)).isoformat()
        ScheduleModel.create(self.proj, "Soon milestone", soon, conn=self.conn)

        from src.services.notification_service import check_upcoming_deadlines
        upcoming = check_upcoming_deadlines(7, self.conn)
        self.assertGreaterEqual(len(upcoming), 1)


class TestChartWidgets(unittest.TestCase):
    def test_chart_widgets_importable(self):
        """차트 위젯 임포트 테스트"""
        from src.widgets.chart_widgets import PieChartWidget, BarChartWidget, GaugeWidget
        self.assertTrue(callable(PieChartWidget))
        self.assertTrue(callable(BarChartWidget))
        self.assertTrue(callable(GaugeWidget))


class TestDarkMode(unittest.TestCase):
    def test_get_stylesheet(self):
        """테마 스타일시트 반환 테스트"""
        from src.utils.styles import get_stylesheet, MAIN_STYLESHEET
        light = get_stylesheet("light")
        dark = get_stylesheet("dark")
        self.assertIsInstance(light, str)
        self.assertIsInstance(dark, str)
        self.assertNotEqual(light, dark)
        self.assertEqual(light, MAIN_STYLESHEET)


if __name__ == "__main__":
    unittest.main()
