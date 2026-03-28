"""프로젝트 관리 서비스"""
from src.models.oem import OemModel
from src.models.project import ProjectModel
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.checklist import ChecklistModel
from src.services.oem_config_service import load_oem_config, get_stage_config
from src.utils.constants import SWE_STAGES, ProjectStatus, StageStatus


def create_project_from_template(oem_id, project_name, description="", conn=None,
                                 start_date=None, target_end_date=None,
                                 initial_phase_name=None):
    """OEM 설정 템플릿을 기반으로 프로젝트를 생성하고 모든 단계/문서/체크리스트를 초기화

    OEM의 config_yaml을 파싱하여 각 SWE 단계에 대해:
      - Stage 레코드 생성
      - required_documents에 따라 Document 레코드 생성
      - checklist에 따라 ChecklistItem 레코드 생성

    Args:
        oem_id: OEM ID
        project_name: 프로젝트 이름
        description: 프로젝트 설명
        conn: SQLite 연결 객체

    Returns:
        int: 생성된 프로젝트 ID

    Raises:
        ValueError: OEM이 존재하지 않거나 설정이 없는 경우
    """
    from src.models.database import get_connection
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    # OEM 조회
    oem = OemModel.get_by_id(oem_id, conn=conn)
    if not oem:
        raise ValueError(f"OEM with id {oem_id} not found")

    config_yaml = oem["config_yaml"]
    if not config_yaml or not config_yaml.strip():
        # 설정이 없으면 기본 generic 설정 사용
        oem_config = {"stages": {swe: {"enabled": True} for swe in SWE_STAGES}}
    else:
        oem_config = load_oem_config(config_yaml)

    # 프로젝트 생성
    project_id = ProjectModel.create(
        oem_id=oem_id,
        name=project_name,
        description=description,
        status=ProjectStatus.ACTIVE,
        start_date=start_date,
        target_end_date=target_end_date,
        conn=conn,
    )

    # Phase 생성 후 Phase 아래에 SWE 단계 생성
    from src.services.phase_service import create_phase_from_template

    # OEM config에서 첫 번째 Phase 이름 가져오기
    initial_phase = initial_phase_name
    if not initial_phase:
        oem_phases = oem_config.get("phases", [])
        initial_phase = oem_phases[0] if oem_phases else "Phase 1"

    create_phase_from_template(project_id, initial_phase, conn=conn)

    if should_close:
        conn.close()

    return project_id


def get_project_summary(project_id, conn):
    """프로젝트 요약 정보를 단계별 완료 통계와 함께 반환

    Args:
        project_id: 프로젝트 ID
        conn: SQLite 연결 객체

    Returns:
        dict: 프로젝트 요약 정보
            - project: 프로젝트 기본 정보 (dict)
            - oem_name: OEM 이름
            - stages: 단계별 정보 리스트
            - overall_progress: 전체 진행률 (0~100)

    Raises:
        ValueError: 프로젝트가 존재하지 않는 경우
    """
    project = ProjectModel.get_by_id(project_id, conn=conn)
    if not project:
        raise ValueError(f"Project with id {project_id} not found")

    # OEM 정보
    oem = OemModel.get_by_id(project["oem_id"], conn=conn)
    oem_name = oem["name"] if oem else "Unknown"

    # 단계별 통계 수집
    stages = StageModel.get_by_project(project_id, conn=conn)
    stage_summaries = []
    total_overall = 0.0

    for stage in stages:
        stats = StageModel.get_completion_stats(stage["id"], conn=conn)
        swe_info = SWE_STAGES.get(stage["swe_level"], {})
        stage_summaries.append({
            "id": stage["id"],
            "swe_level": stage["swe_level"],
            "name_en": swe_info.get("name_en", stage["swe_level"]),
            "name_ko": swe_info.get("name_ko", stage["swe_level"]),
            "status": stage["status"],
            "checklist_total": stats["checklist_total"],
            "checklist_checked": stats["checklist_checked"],
            "checklist_pct": stats["checklist_pct"],
            "doc_total": stats["doc_total"],
            "doc_approved": stats["doc_approved"],
            "doc_pct": stats["doc_pct"],
            "overall_pct": stats["overall_pct"],
        })
        total_overall += stats["overall_pct"]

    num_stages = len(stage_summaries)
    overall_progress = (total_overall / num_stages) if num_stages > 0 else 0.0

    return {
        "project": {
            "id": project["id"],
            "name": project["name"],
            "description": project["description"],
            "status": project["status"],
            "start_date": project["start_date"],
            "target_end_date": project["target_end_date"],
        },
        "oem_name": oem_name,
        "stages": stage_summaries,
        "overall_progress": round(overall_progress, 1),
    }
