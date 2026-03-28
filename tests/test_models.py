"""데이터 모델 CRUD 테스트"""
import os
import sys
import sqlite3
import unittest

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import get_connection, initialize_schema
from src.models.oem import OemModel
from src.models.project import ProjectModel
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.checklist import ChecklistModel
from src.models.traceability import TraceabilityModel
from src.models.schedule import ScheduleModel


class TestModels(unittest.TestCase):
    def setUp(self):
        """각 테스트마다 인메모리 DB 생성"""
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        initialize_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_create_oem(self):
        """OEM 생성 및 조회 테스트"""
        oem_id = OemModel.create("TestOEM", "Test Description", "config: test", self.conn)
        self.assertIsNotNone(oem_id)

        oem = OemModel.get_by_id(oem_id, self.conn)
        self.assertEqual(oem["name"], "TestOEM")
        self.assertEqual(oem["description"], "Test Description")
        self.assertEqual(oem["config_yaml"], "config: test")

    def test_get_all_oems(self):
        """전체 OEM 조회 테스트"""
        OemModel.create("OEM_A", conn=self.conn)
        OemModel.create("OEM_B", conn=self.conn)
        oems = OemModel.get_all(self.conn)
        self.assertEqual(len(oems), 2)

    def test_update_oem(self):
        """OEM 업데이트 테스트"""
        oem_id = OemModel.create("OldName", conn=self.conn)
        OemModel.update(oem_id, name="NewName", conn=self.conn)
        oem = OemModel.get_by_id(oem_id, self.conn)
        self.assertEqual(oem["name"], "NewName")

    def test_delete_oem(self):
        """OEM 삭제 테스트"""
        oem_id = OemModel.create("ToDelete", conn=self.conn)
        OemModel.delete(oem_id, self.conn)
        oem = OemModel.get_by_id(oem_id, self.conn)
        self.assertIsNone(oem)

    def test_create_project_with_stages(self):
        """프로젝트 생성 시 SWE.1~SWE.6 자동 생성 확인"""
        oem_id = OemModel.create("TestOEM", conn=self.conn)
        proj_id = ProjectModel.create(oem_id, "Test Project", conn=self.conn)

        # 6개 단계 생성
        for swe in ["SWE.1", "SWE.2", "SWE.3", "SWE.4", "SWE.5", "SWE.6"]:
            StageModel.create(proj_id, swe, conn=self.conn)

        stages = StageModel.get_by_project(proj_id, self.conn)
        self.assertEqual(len(stages), 6)
        self.assertEqual(stages[0]["swe_level"], "SWE.1")
        self.assertEqual(stages[5]["swe_level"], "SWE.6")

    def test_project_by_oem(self):
        """OEM별 프로젝트 조회"""
        oem1 = OemModel.create("OEM1", conn=self.conn)
        oem2 = OemModel.create("OEM2", conn=self.conn)
        ProjectModel.create(oem1, "P1", conn=self.conn)
        ProjectModel.create(oem1, "P2", conn=self.conn)
        ProjectModel.create(oem2, "P3", conn=self.conn)

        projects_1 = ProjectModel.get_by_oem(oem1, self.conn)
        projects_2 = ProjectModel.get_by_oem(oem2, self.conn)
        self.assertEqual(len(projects_1), 2)
        self.assertEqual(len(projects_2), 1)

    def test_document_status_transition(self):
        """Draft → In Review → Approved 상태 전이"""
        oem_id = OemModel.create("OEM", conn=self.conn)
        proj_id = ProjectModel.create(oem_id, "Proj", conn=self.conn)
        stage_id = StageModel.create(proj_id, "SWE.1", conn=self.conn)
        doc_id = DocumentModel.create(stage_id, "SRS", status="Draft", conn=self.conn)

        # Draft → In Review
        DocumentModel.update(doc_id, status="In Review", conn=self.conn)
        doc = DocumentModel.get_by_id(doc_id, self.conn)
        self.assertEqual(doc["status"], "In Review")

        # In Review → Approved
        DocumentModel.update(doc_id, status="Approved", conn=self.conn)
        doc = DocumentModel.get_by_id(doc_id, self.conn)
        self.assertEqual(doc["status"], "Approved")

    def test_checklist_toggle(self):
        """체크리스트 토글 테스트"""
        oem_id = OemModel.create("OEM", conn=self.conn)
        proj_id = ProjectModel.create(oem_id, "Proj", conn=self.conn)
        stage_id = StageModel.create(proj_id, "SWE.1", conn=self.conn)
        item_id = ChecklistModel.create(stage_id, "Test item", self.conn)

        # 초기: 미체크
        items = ChecklistModel.get_by_stage(stage_id, self.conn)
        self.assertEqual(items[0]["is_checked"], 0)

        # 토글: 체크
        ChecklistModel.toggle(item_id, "Tester", self.conn)
        items = ChecklistModel.get_by_stage(stage_id, self.conn)
        self.assertEqual(items[0]["is_checked"], 1)

        # 토글: 다시 미체크
        ChecklistModel.toggle(item_id, "", self.conn)
        items = ChecklistModel.get_by_stage(stage_id, self.conn)
        self.assertEqual(items[0]["is_checked"], 0)

    def test_traceability_link_creation(self):
        """문서 간 추적성 링크 생성 및 조회"""
        oem_id = OemModel.create("OEM", conn=self.conn)
        proj_id = ProjectModel.create(oem_id, "Proj", conn=self.conn)
        stage1 = StageModel.create(proj_id, "SWE.1", conn=self.conn)
        stage6 = StageModel.create(proj_id, "SWE.6", conn=self.conn)

        doc1 = DocumentModel.create(stage1, "SRS", conn=self.conn)
        doc6 = DocumentModel.create(stage6, "QT Report", conn=self.conn)

        link_id = TraceabilityModel.create(doc1, doc6, "verifies", "Test link", self.conn)
        self.assertIsNotNone(link_id)

        links = TraceabilityModel.get_by_document(doc1, self.conn)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["link_type"], "verifies")

    def test_traceability_completeness(self):
        """추적성 완성도 계산 테스트"""
        oem_id = OemModel.create("OEM", conn=self.conn)
        proj_id = ProjectModel.create(oem_id, "Proj", conn=self.conn)
        stage1 = StageModel.create(proj_id, "SWE.1", conn=self.conn)
        stage6 = StageModel.create(proj_id, "SWE.6", conn=self.conn)

        doc1a = DocumentModel.create(stage1, "SRS", conn=self.conn)
        doc1b = DocumentModel.create(stage1, "Req Review", conn=self.conn)
        doc6a = DocumentModel.create(stage6, "QT Plan", conn=self.conn)

        # 링크 없음 → 0%
        result = TraceabilityModel.get_completeness_for_pair(stage1, stage6, self.conn)
        self.assertEqual(result["completeness_pct"], 0)

        # 1개 링크
        TraceabilityModel.create(doc1a, doc6a, "verifies", conn=self.conn)
        result = TraceabilityModel.get_completeness_for_pair(stage1, stage6, self.conn)
        self.assertGreater(result["completeness_pct"], 0)
        self.assertEqual(result["link_count"], 1)

    def test_stage_completion_stats(self):
        """단계 완료율 통계 테스트"""
        oem_id = OemModel.create("OEM", conn=self.conn)
        proj_id = ProjectModel.create(oem_id, "Proj", conn=self.conn)
        stage_id = StageModel.create(proj_id, "SWE.1", conn=self.conn)

        # 문서 2개, 1개 Approved
        doc1 = DocumentModel.create(stage_id, "Doc1", status="Approved", conn=self.conn)
        doc2 = DocumentModel.create(stage_id, "Doc2", status="Draft", conn=self.conn)

        # 체크리스트 3개, 2개 체크
        c1 = ChecklistModel.create(stage_id, "Item1", self.conn)
        c2 = ChecklistModel.create(stage_id, "Item2", self.conn)
        c3 = ChecklistModel.create(stage_id, "Item3", self.conn)
        ChecklistModel.toggle(c1, "User", self.conn)
        ChecklistModel.toggle(c2, "User", self.conn)

        stats = StageModel.get_completion_stats(stage_id, self.conn)
        self.assertEqual(stats["doc_total"], 2)
        self.assertEqual(stats["doc_approved"], 1)
        self.assertAlmostEqual(stats["doc_pct"], 50.0)
        self.assertEqual(stats["checklist_total"], 3)
        self.assertEqual(stats["checklist_checked"], 2)
        self.assertAlmostEqual(stats["checklist_pct"], 66.67, places=1)

    def test_schedule_milestones(self):
        """마일스톤 CRUD 테스트"""
        oem_id = OemModel.create("OEM", conn=self.conn)
        proj_id = ProjectModel.create(oem_id, "Proj", conn=self.conn)

        ms_id = ScheduleModel.create(proj_id, "Milestone 1", "2026-06-01", conn=self.conn)
        milestones = ScheduleModel.get_by_project(proj_id, self.conn)
        self.assertEqual(len(milestones), 1)
        self.assertEqual(milestones[0]["name"], "Milestone 1")

        ScheduleModel.update(ms_id, status="Completed", conn=self.conn)
        milestones = ScheduleModel.get_by_project(proj_id, self.conn)
        self.assertEqual(milestones[0]["status"], "Completed")

    def test_cascade_delete(self):
        """OEM 삭제 시 하위 데이터 연쇄 삭제"""
        oem_id = OemModel.create("OEM", conn=self.conn)
        proj_id = ProjectModel.create(oem_id, "Proj", conn=self.conn)
        stage_id = StageModel.create(proj_id, "SWE.1", conn=self.conn)
        DocumentModel.create(stage_id, "Doc", conn=self.conn)
        ChecklistModel.create(stage_id, "Item", self.conn)

        OemModel.delete(oem_id, self.conn)

        self.assertIsNone(ProjectModel.get_by_id(proj_id, self.conn))
        self.assertEqual(len(StageModel.get_by_project(proj_id, self.conn)), 0)


if __name__ == "__main__":
    unittest.main()
