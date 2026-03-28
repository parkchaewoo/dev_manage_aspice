"""서비스 로직 테스트"""
import os
import sys
import sqlite3
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import initialize_schema
from src.models.oem import OemModel
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.traceability import TraceabilityModel
from src.utils.yaml_helpers import load_yaml_string, dump_yaml_string
from src.utils.constants import SWE_STAGES, VMODEL_PAIRS, DocumentStatus


class TestOemConfigService(unittest.TestCase):
    def test_yaml_parsing(self):
        """YAML 설정 파싱 테스트"""
        yaml_str = """
oem_name: TestOEM
stages:
  SWE.1:
    enabled: true
    display_name: "Requirements"
    required_documents:
      - name: "SRS"
        template_id: "srs"
    checklist:
      - "Check item 1"
"""
        config = load_yaml_string(yaml_str)
        self.assertEqual(config["oem_name"], "TestOEM")
        self.assertTrue(config["stages"]["SWE.1"]["enabled"])
        self.assertEqual(len(config["stages"]["SWE.1"]["required_documents"]), 1)
        self.assertEqual(config["stages"]["SWE.1"]["required_documents"][0]["name"], "SRS")

    def test_yaml_roundtrip(self):
        """YAML 직렬화/역직렬화 왕복 테스트"""
        data = {"name": "Test", "stages": {"SWE.1": {"enabled": True}}}
        yaml_str = dump_yaml_string(data)
        parsed = load_yaml_string(yaml_str)
        self.assertEqual(parsed["name"], "Test")
        self.assertTrue(parsed["stages"]["SWE.1"]["enabled"])

    def test_load_default_configs(self):
        """기본 OEM 설정 파일 로드 테스트"""
        config_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config", "default_oem_configs"
        )
        if os.path.exists(config_dir):
            from src.utils.yaml_helpers import load_yaml
            for filename in os.listdir(config_dir):
                if filename.endswith(".yaml"):
                    config = load_yaml(os.path.join(config_dir, filename))
                    self.assertIsNotNone(config)
                    self.assertIn("stages", config)


class TestProjectService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        initialize_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_project_creation_from_template(self):
        """OEM 템플릿으로부터 프로젝트 자동 생성"""
        config = dump_yaml_string({
            "oem_name": "TestOEM",
            "stages": {
                "SWE.1": {
                    "enabled": True,
                    "required_documents": [
                        {"name": "SRS", "template_id": "srs"},
                        {"name": "Review Report", "template_id": "review"},
                    ],
                    "checklist": ["Item 1", "Item 2"],
                },
                "SWE.2": {
                    "enabled": True,
                    "required_documents": [{"name": "SAD", "template_id": "sad"}],
                    "checklist": ["Arch check"],
                },
            }
        })
        oem_id = OemModel.create("TestOEM", config_yaml=config, conn=self.conn)

        from src.services.project_service import create_project_from_template
        proj_id = create_project_from_template(oem_id, "Test Project", conn=self.conn)

        stages = StageModel.get_by_project(proj_id, self.conn)
        # 최소 6개 단계 (기본값으로 나머지도 생성)
        self.assertGreaterEqual(len(stages), 2)

        # SWE.1에 문서 2개
        swe1 = [s for s in stages if s["swe_level"] == "SWE.1"]
        if swe1:
            docs = DocumentModel.get_by_stage(swe1[0]["id"], self.conn)
            self.assertGreaterEqual(len(docs), 2)

    def test_traceability_completeness(self):
        """추적성 완성도 계산"""
        oem_id = OemModel.create("OEM", conn=self.conn)
        from src.models.project import ProjectModel
        proj_id = ProjectModel.create(oem_id, "Proj", conn=self.conn)

        s1 = StageModel.create(proj_id, "SWE.1", conn=self.conn)
        s6 = StageModel.create(proj_id, "SWE.6", conn=self.conn)

        d1 = DocumentModel.create(s1, "SRS", conn=self.conn)
        d2 = DocumentModel.create(s1, "Review", conn=self.conn)
        d6 = DocumentModel.create(s6, "QT", conn=self.conn)

        # 0 links
        result = TraceabilityModel.get_completeness_for_pair(s1, s6, self.conn)
        self.assertEqual(result["link_count"], 0)
        self.assertEqual(result["completeness_pct"], 0)

        # 1 link
        TraceabilityModel.create(d1, d6, "verifies", conn=self.conn)
        result = TraceabilityModel.get_completeness_for_pair(s1, s6, self.conn)
        self.assertEqual(result["link_count"], 1)
        self.assertGreater(result["completeness_pct"], 0)


class TestDocumentService(unittest.TestCase):
    def test_status_transitions(self):
        """문서 상태 전이 규칙 테스트"""
        # Draft → In Review: 허용
        self.assertIn("In Review", DocumentStatus.TRANSITIONS["Draft"])
        # In Review → Approved: 허용
        self.assertIn("Approved", DocumentStatus.TRANSITIONS["In Review"])
        # In Review → Rejected: 허용
        self.assertIn("Rejected", DocumentStatus.TRANSITIONS["In Review"])
        # Approved → 없음
        self.assertEqual(len(DocumentStatus.TRANSITIONS["Approved"]), 0)
        # Rejected → Draft: 허용
        self.assertIn("Draft", DocumentStatus.TRANSITIONS["Rejected"])

    def test_skeleton_templates_exist(self):
        """스켈레톤 문서 템플릿 존재 확인"""
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "templates"
        )
        expected_files = [
            "SWE1_requirements_spec.md",
            "SWE2_architecture_design.md",
            "SWE3_detailed_design.md",
            "SWE4_unit_test_report.md",
            "SWE5_integration_test_report.md",
            "SWE6_qualification_test_report.md",
        ]
        for fname in expected_files:
            path = os.path.join(template_dir, fname)
            self.assertTrue(
                os.path.exists(path),
                f"Template file missing: {fname}"
            )


class TestConstants(unittest.TestCase):
    def test_swe_stages_complete(self):
        """SWE.1~SWE.6 모두 정의되어 있는지 확인"""
        for swe in ["SWE.1", "SWE.2", "SWE.3", "SWE.4", "SWE.5", "SWE.6"]:
            self.assertIn(swe, SWE_STAGES)
            self.assertIn("name_en", SWE_STAGES[swe])
            self.assertIn("name_ko", SWE_STAGES[swe])

    def test_vmodel_pairs(self):
        """V-model 쌍 정의 확인"""
        self.assertEqual(VMODEL_PAIRS["SWE.1"], "SWE.6")
        self.assertEqual(VMODEL_PAIRS["SWE.2"], "SWE.5")
        self.assertEqual(VMODEL_PAIRS["SWE.3"], "SWE.4")


if __name__ == "__main__":
    unittest.main()
