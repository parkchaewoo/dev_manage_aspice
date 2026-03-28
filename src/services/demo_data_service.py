"""데모 데이터 서비스 - 기본 OEM 3개 + 예시 프로젝트 3개 생성"""
import os
from src.models.oem import OemModel
from src.models.project import ProjectModel
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.checklist import ChecklistModel
from src.models.traceability import TraceabilityModel
from src.models.schedule import ScheduleModel
from src.utils.constants import SWE_STAGES
from src.utils.yaml_helpers import load_yaml, dump_yaml_string


def _load_oem_yaml(filename):
    """config/default_oem_configs/에서 YAML 로드"""
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base, "config", "default_oem_configs", filename)
    try:
        data = load_yaml(path)
        return dump_yaml_string(data)
    except Exception:
        return ""


def _create_stages_from_config(project_id, config_yaml_str, conn):
    """OEM 설정에 기반하여 단계/문서/체크리스트 생성"""
    from src.utils.yaml_helpers import load_yaml_string
    config = load_yaml_string(config_yaml_str) if config_yaml_str else {}
    stages_config = config.get("stages", {})

    stage_ids = {}
    doc_ids = {}

    for swe_level in ["SWE.1", "SWE.2", "SWE.3", "SWE.4", "SWE.5", "SWE.6"]:
        stage_conf = stages_config.get(swe_level, {})
        if stage_conf.get("enabled", True) is False:
            continue

        stage_id = StageModel.create(project_id, swe_level, conn=conn)
        stage_ids[swe_level] = stage_id

        # 문서 생성
        docs = stage_conf.get("required_documents", [])
        if not docs:
            # 기본 문서
            default_docs = {
                "SWE.1": [("Software Requirements Specification (SRS)", "srs"),
                          ("Requirements Review Report", "req_review")],
                "SWE.2": [("Software Architecture Document (SAD)", "sad"),
                          ("Interface Design Document", "idd")],
                "SWE.3": [("Software Detailed Design (SDD)", "sdd"),
                          ("Source Code", "code")],
                "SWE.4": [("Unit Test Plan", "ut_plan"),
                          ("Unit Test Report", "ut_report")],
                "SWE.5": [("Integration Test Plan", "it_plan"),
                          ("Integration Test Report", "it_report")],
                "SWE.6": [("Qualification Test Plan", "qt_plan"),
                          ("Qualification Test Report", "qt_report")],
            }
            docs = [{"name": n, "template_id": t} for n, t in default_docs.get(swe_level, [])]

        swe_doc_ids = []
        for doc_info in docs:
            doc_name = doc_info.get("name", "Unnamed Document")
            template_id = doc_info.get("template_id", "")
            did = DocumentModel.create(stage_id, doc_name, template_type=template_id, conn=conn)
            swe_doc_ids.append(did)
        doc_ids[swe_level] = swe_doc_ids

        # 체크리스트 생성
        checklist = stage_conf.get("checklist", [])
        if not checklist:
            default_checklists = {
                "SWE.1": ["All requirements have unique IDs / 모든 요구사항에 고유 ID 부여",
                          "Requirements are testable / 요구사항 시험 가능성 확인",
                          "Traceability to system requirements / 시스템 요구사항 추적성 확인",
                          "Review completed / 검토 완료"],
                "SWE.2": ["Architecture addresses all requirements / 아키텍처가 모든 요구사항을 반영",
                          "Interface descriptions complete / 인터페이스 기술 완료",
                          "Resource constraints considered / 리소스 제약 고려",
                          "Review completed / 검토 완료"],
                "SWE.3": ["Detailed design matches architecture / 상세 설계가 아키텍처와 일치",
                          "Coding guidelines followed / 코딩 가이드라인 준수",
                          "Static analysis passed / 정적 분석 통과",
                          "Code review completed / 코드 리뷰 완료"],
                "SWE.4": ["Unit test plan reviewed / 단위 시험 계획 검토",
                          "Coverage targets met / 커버리지 목표 달성",
                          "All test cases passed / 모든 테스트 통과",
                          "Test report reviewed / 시험 보고서 검토"],
                "SWE.5": ["Integration strategy defined / 통합 전략 정의",
                          "Interface tests passed / 인터페이스 시험 통과",
                          "Timing requirements met / 타이밍 요구사항 충족",
                          "Integration report reviewed / 통합 보고서 검토"],
                "SWE.6": ["All requirements covered / 모든 요구사항 커버",
                          "Test environment validated / 시험 환경 검증",
                          "All test cases executed / 모든 시험 실행",
                          "Qualification report approved / 적격성 보고서 승인"],
            }
            checklist = default_checklists.get(swe_level, [])

        for item in checklist:
            ChecklistModel.create(stage_id, item, conn=conn)

    return stage_ids, doc_ids


def create_demo_data(conn):
    """데모 데이터 생성"""
    # === OEM 생성 ===
    hkmc_yaml = _load_oem_yaml("hkmc.yaml")
    vw_yaml = _load_oem_yaml("volkswagen.yaml")
    gm_yaml = _load_oem_yaml("gm.yaml")

    hkmc_id = OemModel.create("HKMC", "현대기아자동차그룹 / Hyundai Kia Motor Company", hkmc_yaml, conn)
    vw_id = OemModel.create("Volkswagen", "Volkswagen Group", vw_yaml, conn)
    gm_id = OemModel.create("GM", "General Motors", gm_yaml, conn)

    # === 프로젝트 1: HKMC 조향 시스템 ===
    proj1_id = ProjectModel.create(
        hkmc_id, "조향 시스템 (Steering System)",
        "EPS 전동 조향 시스템 소프트웨어 개발",
        "Active", "2026-01-15", "2026-12-31", conn
    )
    stage_ids_1, doc_ids_1 = _create_stages_from_config(proj1_id, hkmc_yaml, conn)

    # SWE.1 완료, SWE.2 진행중
    if "SWE.1" in stage_ids_1:
        StageModel.update(stage_ids_1["SWE.1"], status="Completed", conn=conn)
        for did in doc_ids_1.get("SWE.1", []):
            DocumentModel.update(did, status="Approved", conn=conn)
        # 체크리스트 모두 체크
        items = ChecklistModel.get_by_stage(stage_ids_1["SWE.1"], conn)
        for item in items:
            ChecklistModel.toggle(item["id"], "Demo User", conn)

    if "SWE.2" in stage_ids_1:
        StageModel.update(stage_ids_1["SWE.2"], status="In Progress", conn=conn)
        docs = doc_ids_1.get("SWE.2", [])
        if docs:
            DocumentModel.update(docs[0], status="In Review", conn=conn)

    # 추적성 링크: SWE.1 ↔ SWE.6
    if doc_ids_1.get("SWE.1") and doc_ids_1.get("SWE.6"):
        TraceabilityModel.create(
            doc_ids_1["SWE.1"][0], doc_ids_1["SWE.6"][0],
            "verifies", "요구사항 적격성 시험 추적", conn
        )
        if len(doc_ids_1["SWE.1"]) > 1 and len(doc_ids_1["SWE.6"]) > 1:
            TraceabilityModel.create(
                doc_ids_1["SWE.1"][1], doc_ids_1["SWE.6"][1],
                "verifies", "검토 보고서 추적", conn
            )

    # SWE.2 ↔ SWE.5
    if doc_ids_1.get("SWE.2") and doc_ids_1.get("SWE.5"):
        TraceabilityModel.create(
            doc_ids_1["SWE.2"][0], doc_ids_1["SWE.5"][0],
            "verifies", "아키텍처 통합 시험 추적", conn
        )

    # SWE.3 ↔ SWE.4
    if doc_ids_1.get("SWE.3") and doc_ids_1.get("SWE.4"):
        TraceabilityModel.create(
            doc_ids_1["SWE.3"][0], doc_ids_1["SWE.4"][0],
            "verifies", "상세 설계 단위 검증 추적", conn
        )

    # 마일스톤
    ScheduleModel.create(proj1_id, "SWE.1 Requirements Complete", "2026-03-01",
                         stage_ids_1.get("SWE.1"), "Completed", conn)
    ScheduleModel.create(proj1_id, "SWE.2 Architecture Review", "2026-05-01",
                         stage_ids_1.get("SWE.2"), "Pending", conn)
    ScheduleModel.create(proj1_id, "SWE.6 Final Qualification", "2026-11-30",
                         stage_ids_1.get("SWE.6"), "Pending", conn)

    # === 프로젝트 2: VW BRAKE 시스템 ===
    proj2_id = ProjectModel.create(
        vw_id, "BRAKE System (브레이크 시스템)",
        "ABS/ESC 브레이크 제어 시스템 소프트웨어",
        "Active", "2026-02-01", "2027-03-31", conn
    )
    stage_ids_2, doc_ids_2 = _create_stages_from_config(proj2_id, vw_yaml, conn)

    # SWE.1 완료, SWE.2 완료, SWE.3 진행중
    for swe in ["SWE.1", "SWE.2"]:
        if swe in stage_ids_2:
            StageModel.update(stage_ids_2[swe], status="Completed", conn=conn)
            for did in doc_ids_2.get(swe, []):
                DocumentModel.update(did, status="Approved", conn=conn)
            items = ChecklistModel.get_by_stage(stage_ids_2[swe], conn)
            for item in items:
                ChecklistModel.toggle(item["id"], "VW Engineer", conn)

    if "SWE.3" in stage_ids_2:
        StageModel.update(stage_ids_2["SWE.3"], status="In Progress", conn=conn)

    # 추적성 링크
    if doc_ids_2.get("SWE.1") and doc_ids_2.get("SWE.6"):
        TraceabilityModel.create(
            doc_ids_2["SWE.1"][0], doc_ids_2["SWE.6"][0],
            "verifies", "Requirements to qualification test", conn
        )
    if doc_ids_2.get("SWE.2") and doc_ids_2.get("SWE.5"):
        TraceabilityModel.create(
            doc_ids_2["SWE.2"][0], doc_ids_2["SWE.5"][0],
            "verifies", "Architecture to integration test", conn
        )

    ScheduleModel.create(proj2_id, "SWE.1 Complete", "2026-04-15",
                         stage_ids_2.get("SWE.1"), "Completed", conn)
    ScheduleModel.create(proj2_id, "SWE.3 Code Freeze", "2026-08-01",
                         stage_ids_2.get("SWE.3"), "Pending", conn)

    # === 프로젝트 3: GM Navigation ===
    proj3_id = ProjectModel.create(
        gm_id, "Navigation System (네비게이션)",
        "차량 내비게이션 소프트웨어 개발",
        "Active", "2026-03-01", "2027-06-30", conn
    )
    stage_ids_3, doc_ids_3 = _create_stages_from_config(proj3_id, gm_yaml, conn)

    # SWE.1만 진행중
    if "SWE.1" in stage_ids_3:
        StageModel.update(stage_ids_3["SWE.1"], status="In Progress", conn=conn)
        docs = doc_ids_3.get("SWE.1", [])
        if docs:
            DocumentModel.update(docs[0], status="In Review", conn=conn)

    ScheduleModel.create(proj3_id, "SWE.1 Requirements Review", "2026-05-15",
                         stage_ids_3.get("SWE.1"), "Pending", conn)
    ScheduleModel.create(proj3_id, "Project Kickoff Complete", "2026-03-15",
                         None, "Completed", conn)

    conn.commit()
