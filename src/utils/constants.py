"""ASPICE 프로세스 관리 상수 정의"""

APP_NAME = "ASPICE Process Manager"
APP_VERSION_FILE = "VERSION"

# SWE 단계 정의
SWE_STAGES = {
    "SWE.1": {
        "name_en": "Software Requirements Analysis",
        "name_ko": "소프트웨어 요구사항 분석",
        "description_en": "Derive and document software requirements from system requirements.",
        "description_ko": "시스템 요구사항으로부터 소프트웨어 요구사항을 도출하고 문서화합니다.",
        "side": "left",
        "level": 1,
    },
    "SWE.2": {
        "name_en": "Software Architectural Design",
        "name_ko": "소프트웨어 아키텍처 설계",
        "description_en": "Design the software architecture from software requirements.",
        "description_ko": "소프트웨어 요구사항으로부터 소프트웨어 아키텍처를 설계합니다.",
        "side": "left",
        "level": 2,
    },
    "SWE.3": {
        "name_en": "Software Detailed Design and Unit Construction",
        "name_ko": "소프트웨어 상세 설계 및 단위 구현",
        "description_en": "Create detailed design and implement software units.",
        "description_ko": "상세 설계를 작성하고 소프트웨어 단위를 구현합니다.",
        "side": "left",
        "level": 3,
    },
    "SWE.4": {
        "name_en": "Software Unit Verification",
        "name_ko": "소프트웨어 단위 검증",
        "description_en": "Verify software units against the detailed design.",
        "description_ko": "상세 설계에 대해 소프트웨어 단위를 검증합니다.",
        "side": "right",
        "level": 3,
    },
    "SWE.5": {
        "name_en": "Software Integration and Integration Test",
        "name_ko": "소프트웨어 통합 및 통합 시험",
        "description_en": "Integrate software units and test the integrated software.",
        "description_ko": "소프트웨어 단위를 통합하고 통합된 소프트웨어를 시험합니다.",
        "side": "right",
        "level": 2,
    },
    "SWE.6": {
        "name_en": "Software Qualification Test",
        "name_ko": "소프트웨어 적격성 시험",
        "description_en": "Test the integrated software against the software requirements.",
        "description_ko": "소프트웨어 요구사항에 대해 통합된 소프트웨어를 시험합니다.",
        "side": "right",
        "level": 1,
    },
}

# V-model 쌍 (검증 관계: 좌↔우)
VMODEL_PAIRS = {
    "SWE.1": "SWE.6",
    "SWE.2": "SWE.5",
    "SWE.3": "SWE.4",
}

# 순차적 도출 쌍 (개발/검증 흐름)
SEQUENTIAL_PAIRS = {
    "SWE.1": "SWE.2",  # Requirements → Architecture
    "SWE.2": "SWE.3",  # Architecture → Detailed Design
    "SWE.3": "SWE.4",  # Detailed Design → Unit Verification
    "SWE.4": "SWE.5",  # Unit Verification → Integration Test
    "SWE.5": "SWE.6",  # Integration Test → Qualification Test
}

# 프로젝트 상태
class ProjectStatus:
    ACTIVE = "Active"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"

    ALL = [ACTIVE, COMPLETED, ON_HOLD]

# 단계 상태
class StageStatus:
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    COMPLETED = "Completed"

    ALL = [NOT_STARTED, IN_PROGRESS, IN_REVIEW, COMPLETED]

# 문서 상태
class DocumentStatus:
    DRAFT = "Draft"
    IN_REVIEW = "In Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"

    ALL = [DRAFT, IN_REVIEW, APPROVED, REJECTED]

    TRANSITIONS = {
        DRAFT: [IN_REVIEW],
        IN_REVIEW: [APPROVED, REJECTED],
        APPROVED: [],
        REJECTED: [DRAFT],
    }

# 추적성 링크 유형
class LinkType:
    DERIVES = "derives"
    VERIFIES = "verifies"
    SATISFIES = "satisfies"

    ALL = [DERIVES, VERIFIES, SATISFIES]

# 마일스톤 상태
class MilestoneStatus:
    PENDING = "Pending"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"

    ALL = [PENDING, COMPLETED, OVERDUE]

# 상태별 색상
STATUS_COLORS = {
    StageStatus.NOT_STARTED: "#8E8E93",
    StageStatus.IN_PROGRESS: "#007AFF",
    StageStatus.IN_REVIEW: "#FF9500",
    StageStatus.COMPLETED: "#34C759",
    DocumentStatus.DRAFT: "#8E8E93",
    DocumentStatus.IN_REVIEW: "#FF9500",
    DocumentStatus.APPROVED: "#34C759",
    DocumentStatus.REJECTED: "#FF3B30",
    MilestoneStatus.PENDING: "#8E8E93",
    MilestoneStatus.COMPLETED: "#34C759",
    MilestoneStatus.OVERDUE: "#FF3B30",
}
