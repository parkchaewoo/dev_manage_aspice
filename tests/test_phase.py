"""Phase 및 v0.3.0 신규 기능 테스트"""
import os
import sys
import sqlite3
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import get_connection, initialize_schema
from src.models.oem import OemModel
from src.models.project import ProjectModel
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.checklist import ChecklistModel
from src.models.traceability import TraceabilityModel


class TestPhaseModel(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        initialize_schema(self.conn)
        self.oem_id = OemModel.create("TestOEM", conn=self.conn)
        self.proj_id = ProjectModel.create(self.oem_id, "TestProject", conn=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_create_phase(self):
        """Phase 생성 테스트"""
        from src.models.phase import PhaseModel
        phase_id = PhaseModel.create(self.proj_id, "Mcar", conn=self.conn)
        self.assertIsNotNone(phase_id)

        phase = PhaseModel.get_by_id(phase_id, self.conn)
        self.assertEqual(phase["name"], "Mcar")
        self.assertEqual(phase["project_id"], self.proj_id)

    def test_phases_by_project(self):
        """프로젝트별 Phase 목록 조회"""
        from src.models.phase import PhaseModel
        PhaseModel.create(self.proj_id, "P1", phase_order=1, conn=self.conn)
        PhaseModel.create(self.proj_id, "P2", phase_order=2, conn=self.conn)

        phases = PhaseModel.get_by_project(self.proj_id, self.conn)
        self.assertEqual(len(phases), 2)
        self.assertEqual(phases[0]["name"], "P1")
        self.assertEqual(phases[1]["name"], "P2")

    def test_stage_with_phase(self):
        """Phase에 속한 Stage 생성"""
        from src.models.phase import PhaseModel
        phase_id = PhaseModel.create(self.proj_id, "Mcar", conn=self.conn)
        stage_id = StageModel.create(self.proj_id, "SWE.1", phase_id=phase_id, conn=self.conn)

        stage = StageModel.get_by_id(stage_id, self.conn)
        self.assertEqual(stage["phase_id"], phase_id)


class TestPhaseLog(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        initialize_schema(self.conn)
        self.oem_id = OemModel.create("OEM", conn=self.conn)
        self.proj_id = ProjectModel.create(self.oem_id, "Proj", conn=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_create_log(self):
        """Phase 로그 생성 테스트"""
        from src.models.phase import PhaseModel
        from src.models.phase_log import PhaseLogModel
        phase_id = PhaseModel.create(self.proj_id, "P1", conn=self.conn)
        log_id = PhaseLogModel.create(phase_id, "created", "phase", phase_id,
                                       "Phase P1 created", conn=self.conn)
        self.assertIsNotNone(log_id)

        logs = PhaseLogModel.get_by_phase(phase_id, self.conn)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["action"], "created")


class TestPhaseInheritance(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        initialize_schema(self.conn)
        self.oem_id = OemModel.create("HKMC", config_yaml="stages: {}", conn=self.conn)
        self.proj_id = ProjectModel.create(self.oem_id, "Steering", conn=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_inherit_approved_documents(self):
        """이전 Phase의 Approved 문서가 상속되는지 확인"""
        from src.models.phase import PhaseModel

        # Phase 1 생성 + SWE.1 + Approved 문서
        phase1 = PhaseModel.create(self.proj_id, "Mcar", phase_order=1, conn=self.conn)
        stage1 = StageModel.create(self.proj_id, "SWE.1", phase_id=phase1, conn=self.conn)
        doc1 = DocumentModel.create(stage1, "SRS", status="Approved", conn=self.conn)
        doc2 = DocumentModel.create(stage1, "Draft Doc", status="Draft", conn=self.conn)
        ChecklistModel.create(stage1, "Item 1", self.conn)

        # Phase 2 상속
        try:
            from src.services.phase_service import create_phase_inherited
            phase2 = create_phase_inherited(
                self.proj_id, "P1", phase1, conn=self.conn
            )

            # Phase 2의 Stage 확인
            stages2 = StageModel.get_by_phase(phase2, self.conn)
            self.assertGreaterEqual(len(stages2), 1)

            # Approved 문서만 상속되었는지 확인
            if stages2:
                docs2 = DocumentModel.get_by_stage(stages2[0]["id"], self.conn)
                approved_docs = [d for d in docs2 if d["status"] == "Approved"]
                self.assertGreaterEqual(len(approved_docs), 1)
        except ImportError:
            self.skipTest("phase_service not yet implemented")


class TestDocumentCreateFix(unittest.TestCase):
    """문서 생성 버그 수정 확인"""
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        initialize_schema(self.conn)
        oem = OemModel.create("OEM", conn=self.conn)
        proj = ProjectModel.create(oem, "Proj", conn=self.conn)
        self.stage_id = StageModel.create(proj, "SWE.1", conn=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_create_with_reviewer_and_notes(self):
        """reviewer, notes 파라미터로 문서 생성 가능 확인"""
        doc_id = DocumentModel.create(
            self.stage_id, "Test Doc",
            reviewer="John", notes="Test notes",
            conn=self.conn
        )
        doc = DocumentModel.get_by_id(doc_id, self.conn)
        self.assertEqual(doc["reviewer"], "John")
        self.assertEqual(doc["notes"], "Test notes")

    def test_create_with_all_params(self):
        """get_data() 반환값과 동일한 형태로 생성"""
        data = {
            "name": "SRS Document",
            "template_type": "srs",
            "status": "Draft",
            "reviewer": "Reviewer",
            "notes": "Some notes",
        }
        doc_id = DocumentModel.create(self.stage_id, **data, conn=self.conn)
        self.assertIsNotNone(doc_id)


class TestComplianceReport(unittest.TestCase):
    def test_report_generation(self):
        """ASPICE 컴플라이언스 리포트 생성 확인"""
        import tempfile
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        initialize_schema(conn)

        oem = OemModel.create("TestOEM", conn=conn)
        proj = ProjectModel.create(oem, "TestProject", conn=conn)
        stage = StageModel.create(proj, "SWE.1", conn=conn)
        DocumentModel.create(stage, "SRS", status="Approved", conn=conn)

        try:
            from src.services.compliance_report_service import generate_compliance_report
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
                path = f.name
            generate_compliance_report(proj, output_path=path, conn=conn)
            self.assertTrue(os.path.exists(path))
            with open(path, 'r') as f:
                content = f.read()
            self.assertIn("TestProject", content)
            self.assertIn("SWE.1", content)
            os.unlink(path)
        except ImportError:
            self.skipTest("compliance_report_service not yet implemented")

        conn.close()


if __name__ == "__main__":
    unittest.main()
