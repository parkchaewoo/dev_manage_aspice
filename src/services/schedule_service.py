"""일정 및 마일스톤 관리 서비스"""
from datetime import date, datetime, timedelta

from src.models.schedule import ScheduleModel
from src.models.stage import StageModel
from src.models.project import ProjectModel
from src.utils.constants import SWE_STAGES, MilestoneStatus, StageStatus


# 기본 마일스톤 템플릿 (프로젝트 시작일 기준 주 단위 오프셋)
_DEFAULT_MILESTONES = [
    {
        "name": "Project Kickoff",
        "swe_level": None,
        "week_offset": 0,
    },
    {
        "name": "SWE.1 Requirements Baseline",
        "swe_level": "SWE.1",
        "week_offset": 4,
    },
    {
        "name": "SWE.1 Requirements Review",
        "swe_level": "SWE.1",
        "week_offset": 6,
    },
    {
        "name": "SWE.2 Architecture Baseline",
        "swe_level": "SWE.2",
        "week_offset": 10,
    },
    {
        "name": "SWE.2 Architecture Review",
        "swe_level": "SWE.2",
        "week_offset": 12,
    },
    {
        "name": "SWE.3 Detailed Design Complete",
        "swe_level": "SWE.3",
        "week_offset": 18,
    },
    {
        "name": "SWE.3 Code Complete",
        "swe_level": "SWE.3",
        "week_offset": 22,
    },
    {
        "name": "SWE.4 Unit Test Complete",
        "swe_level": "SWE.4",
        "week_offset": 26,
    },
    {
        "name": "SWE.5 Integration Test Start",
        "swe_level": "SWE.5",
        "week_offset": 28,
    },
    {
        "name": "SWE.5 Integration Test Complete",
        "swe_level": "SWE.5",
        "week_offset": 34,
    },
    {
        "name": "SWE.6 Qualification Test Start",
        "swe_level": "SWE.6",
        "week_offset": 36,
    },
    {
        "name": "SWE.6 Qualification Test Complete",
        "swe_level": "SWE.6",
        "week_offset": 42,
    },
    {
        "name": "Software Release",
        "swe_level": None,
        "week_offset": 44,
    },
    {
        "name": "Project Closure",
        "swe_level": None,
        "week_offset": 48,
    },
]


def create_default_milestones(project_id, conn):
    """프로젝트에 기본 마일스톤 세트를 생성

    프로젝트의 start_date를 기준으로 각 마일스톤의 due_date를 계산합니다.
    start_date가 없으면 오늘 날짜를 기준으로 합니다.

    Args:
        project_id: 프로젝트 ID
        conn: SQLite 연결 객체

    Returns:
        list[int]: 생성된 마일스톤 ID 리스트

    Raises:
        ValueError: 프로젝트가 존재하지 않는 경우
    """
    project = ProjectModel.get_by_id(project_id, conn=conn)
    if not project:
        raise ValueError(f"Project with id {project_id} not found")

    # 시작 기준일 결정
    if project["start_date"]:
        try:
            base_date = datetime.strptime(project["start_date"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            base_date = date.today()
    else:
        base_date = date.today()

    # 프로젝트의 단계 매핑 (swe_level -> stage_id)
    stages = StageModel.get_by_project(project_id, conn=conn)
    stage_map = {s["swe_level"]: s["id"] for s in stages}

    milestone_ids = []
    for template in _DEFAULT_MILESTONES:
        due = base_date + timedelta(weeks=template["week_offset"])
        swe_level = template["swe_level"]
        stage_id = stage_map.get(swe_level) if swe_level else None

        mid = ScheduleModel.create(
            project_id=project_id,
            name=template["name"],
            due_date=due.isoformat(),
            stage_id=stage_id,
            status=MilestoneStatus.PENDING,
            conn=conn,
        )
        milestone_ids.append(mid)

    return milestone_ids


def get_overdue_milestones(project_id, conn):
    """기한이 지났지만 완료되지 않은 마일스톤 목록을 반환

    Args:
        project_id: 프로젝트 ID
        conn: SQLite 연결 객체

    Returns:
        list[dict]: 기한 초과 마일스톤 목록 (각 항목은 sqlite3.Row)
    """
    today_str = date.today().isoformat()
    milestones = ScheduleModel.get_by_project(project_id, conn=conn)

    overdue = []
    for m in milestones:
        if m["status"] == MilestoneStatus.COMPLETED:
            continue
        if m["due_date"] and m["due_date"] < today_str:
            overdue.append(m)

    return overdue


def update_milestone_status(milestone_id, conn):
    """마일스톤 상태를 날짜 기반으로 자동 업데이트

    로직:
      - completed_date가 있으면 -> Completed
      - due_date가 오늘 이전이고 미완료 -> Overdue
      - 그 외 -> Pending (변경 없음)

    Args:
        milestone_id: 마일스톤 ID
        conn: SQLite 연결 객체

    Returns:
        str: 업데이트된 상태 문자열

    Raises:
        ValueError: 마일스톤을 찾을 수 없는 경우
    """
    # 마일스톤 직접 조회
    row = conn.execute(
        "SELECT * FROM schedule_milestones WHERE id = ?", (milestone_id,)
    ).fetchone()
    if not row:
        raise ValueError(f"Milestone with id {milestone_id} not found")

    today_str = date.today().isoformat()

    # 완료일이 있으면 완료 처리
    if row["completed_date"]:
        new_status = MilestoneStatus.COMPLETED
    elif row["due_date"] and row["due_date"] < today_str:
        new_status = MilestoneStatus.OVERDUE
    else:
        new_status = MilestoneStatus.PENDING

    # 현재 상태와 다를 때만 업데이트
    if row["status"] != new_status:
        ScheduleModel.update(milestone_id, status=new_status, conn=conn)

    return new_status
