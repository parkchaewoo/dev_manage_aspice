"""문서 관리 서비스"""
from datetime import date

from src.models.document import DocumentModel
from src.models.stage import StageModel
from src.models.project import ProjectModel
from src.models.oem import OemModel
from src.utils.constants import DocumentStatus, SWE_STAGES


# 문서 템플릿 스켈레톤 정의
_SKELETON_TEMPLATES = {
    "SWE1_requirements_spec": {
        "title": "Software Requirements Specification (SRS)",
        "sections": [
            "1. Introduction",
            "  1.1 Purpose",
            "  1.2 Scope",
            "  1.3 Definitions and Acronyms",
            "  1.4 References",
            "2. Overall Description",
            "  2.1 Product Perspective",
            "  2.2 Product Functions Overview",
            "  2.3 User Characteristics",
            "  2.4 Constraints and Assumptions",
            "3. Functional Requirements",
            "  3.1 [FR-001] Requirement Title",
            "    - Description:",
            "    - Source: System Requirement ID",
            "    - Priority: High / Medium / Low",
            "    - Acceptance Criteria:",
            "4. Non-Functional Requirements",
            "  4.1 Performance Requirements",
            "  4.2 Safety Requirements (ASIL level)",
            "  4.3 Memory and Resource Constraints",
            "  4.4 Timing Requirements",
            "5. Interface Requirements",
            "  5.1 Hardware Interfaces",
            "  5.2 Software Interfaces",
            "  5.3 Communication Interfaces (CAN, LIN, Ethernet)",
            "6. Traceability Matrix",
            "7. Revision History",
        ],
    },
    "SWE1_traceability_matrix": {
        "title": "Requirements Traceability Matrix",
        "sections": [
            "1. Introduction",
            "  1.1 Purpose",
            "  1.2 Scope",
            "2. Traceability Matrix",
            "  | System Req ID | SW Req ID | Description | Status | Verification Method |",
            "  |---------------|-----------|-------------|--------|---------------------|",
            "3. Coverage Analysis",
            "  3.1 Forward Traceability (System -> Software)",
            "  3.2 Backward Traceability (Software -> System)",
            "  3.3 Gap Analysis",
            "4. Revision History",
        ],
    },
    "SWE1_analysis_report": {
        "title": "Requirements Analysis Report",
        "sections": [
            "1. Introduction",
            "2. Analysis Methodology",
            "3. Feasibility Assessment",
            "4. Consistency Check Results",
            "5. Completeness Check Results",
            "6. Risk Assessment",
            "7. Open Issues and Recommendations",
            "8. Revision History",
        ],
    },
    "SWE2_architecture_design": {
        "title": "Software Architecture Description (SAD)",
        "sections": [
            "1. Introduction",
            "  1.1 Purpose",
            "  1.2 Scope",
            "  1.3 Architecture Goals and Constraints",
            "2. Architectural Overview",
            "  2.1 System Context Diagram",
            "  2.2 Component Diagram",
            "  2.3 Layered Architecture View",
            "3. Component Descriptions",
            "  3.1 [Component Name]",
            "    - Responsibility:",
            "    - Interfaces Provided:",
            "    - Interfaces Required:",
            "    - Dependencies:",
            "4. Dynamic Behavior",
            "  4.1 Sequence Diagrams",
            "  4.2 State Machine Diagrams",
            "5. Resource Allocation",
            "  5.1 Memory Budget",
            "  5.2 CPU Budget",
            "  5.3 Communication Bandwidth",
            "6. Design Decisions and Rationale",
            "7. Traceability to Requirements",
            "8. Revision History",
        ],
    },
    "SWE2_interface_control": {
        "title": "Interface Control Document (ICD)",
        "sections": [
            "1. Introduction",
            "2. External Interfaces",
            "  2.1 CAN Bus Interfaces",
            "  2.2 LIN Interfaces",
            "  2.3 Ethernet Interfaces",
            "3. Internal Component Interfaces",
            "  3.1 API Definitions",
            "  3.2 Data Types and Structures",
            "  3.3 Error Handling",
            "4. Interface Verification Matrix",
            "5. Revision History",
        ],
    },
    "SWE2_evaluation_report": {
        "title": "Architecture Evaluation Report",
        "sections": [
            "1. Introduction",
            "2. Evaluation Criteria",
            "3. Evaluation Results",
            "4. Identified Risks",
            "5. Recommendations",
            "6. Revision History",
        ],
    },
    "SWE3_detailed_design": {
        "title": "Software Detailed Design Document (SDD)",
        "sections": [
            "1. Introduction",
            "2. Design Conventions",
            "3. Unit Descriptions",
            "  3.1 [Unit Name]",
            "    - Purpose:",
            "    - Algorithm Description:",
            "    - Data Structures:",
            "    - Interface (function signatures):",
            "    - Error Handling:",
            "4. Data Dictionary",
            "5. Traceability to Architecture",
            "6. Revision History",
        ],
    },
    "SWE3_coding_guidelines": {
        "title": "Coding Guidelines Compliance Report",
        "sections": [
            "1. Introduction",
            "2. Applicable Standards (MISRA C, CERT C, AUTOSAR C++14)",
            "3. Compliance Summary",
            "4. Deviations and Justifications",
            "5. Tool Configuration",
            "6. Revision History",
        ],
    },
    "SWE3_static_analysis": {
        "title": "Static Analysis Report",
        "sections": [
            "1. Introduction",
            "2. Tools Used (Polyspace, QAC, Coverity, etc.)",
            "3. Analysis Configuration",
            "4. Results Summary",
            "  4.1 Critical Findings",
            "  4.2 Major Findings",
            "  4.3 Minor Findings",
            "5. Resolution Status",
            "6. Revision History",
        ],
    },
    "SWE4_unit_test_plan": {
        "title": "Unit Test Plan",
        "sections": [
            "1. Introduction",
            "2. Test Strategy",
            "  2.1 Test Approach (white-box / black-box)",
            "  2.2 Coverage Goals (statement, branch, MC/DC)",
            "3. Test Environment",
            "  3.1 Test Framework (Google Test, Unity, etc.)",
            "  3.2 Stubs and Mocks",
            "4. Test Schedule",
            "5. Pass/Fail Criteria",
            "6. Revision History",
        ],
    },
    "SWE4_unit_test_report": {
        "title": "Unit Test Report",
        "sections": [
            "1. Introduction",
            "2. Test Execution Summary",
            "  2.1 Total / Passed / Failed / Blocked",
            "3. Coverage Metrics",
            "  3.1 Statement Coverage",
            "  3.2 Branch Coverage",
            "  3.3 MC/DC Coverage",
            "4. Defect Summary",
            "5. Conclusion and Recommendation",
            "6. Revision History",
        ],
    },
    "SWE4_test_cases": {
        "title": "Unit Test Case Specification",
        "sections": [
            "1. Introduction",
            "2. Test Cases",
            "  2.1 [TC-001] Test Case Title",
            "    - Unit Under Test:",
            "    - Preconditions:",
            "    - Input:",
            "    - Expected Output:",
            "    - Coverage Target:",
            "3. Boundary Value Test Cases",
            "4. Error Injection Test Cases",
            "5. Revision History",
        ],
    },
    "SWE5_integration_test_plan": {
        "title": "Integration Test Plan",
        "sections": [
            "1. Introduction",
            "2. Integration Strategy (top-down, bottom-up, big-bang)",
            "3. Test Environment (HIL, SIL, target board)",
            "4. Interface Test Cases",
            "5. Data Flow Test Cases",
            "6. Schedule and Milestones",
            "7. Pass/Fail Criteria",
            "8. Revision History",
        ],
    },
    "SWE5_integration_test_report": {
        "title": "Integration Test Report",
        "sections": [
            "1. Introduction",
            "2. Test Execution Summary",
            "3. Interface Verification Results",
            "4. Performance Measurements",
            "5. Defect Summary",
            "6. Conclusion",
            "7. Revision History",
        ],
    },
    "SWE5_build_plan": {
        "title": "Integration Build Plan",
        "sections": [
            "1. Introduction",
            "2. Build Strategy",
            "3. Build Order and Dependencies",
            "4. Configuration Management",
            "5. Revision History",
        ],
    },
    "SWE6_qualification_test_plan": {
        "title": "Qualification Test Plan",
        "sections": [
            "1. Introduction",
            "2. Test Objectives",
            "3. Test Environment (target hardware, test bench)",
            "4. Test Cases per Requirement",
            "  4.1 Functional Test Cases",
            "  4.2 Performance Test Cases",
            "  4.3 Robustness Test Cases",
            "5. Pass/Fail Criteria",
            "6. Schedule",
            "7. Revision History",
        ],
    },
    "SWE6_qualification_test_report": {
        "title": "Qualification Test Report",
        "sections": [
            "1. Introduction",
            "2. Test Execution Summary",
            "3. Requirements Verification Status",
            "  | Req ID | Test Case | Result | Notes |",
            "  |--------|-----------|--------|-------|",
            "4. Defect Summary and Disposition",
            "5. Conclusion and Release Recommendation",
            "6. Revision History",
        ],
    },
    "SWE6_release_note": {
        "title": "Release Note",
        "sections": [
            "1. Release Information",
            "  - Version:",
            "  - Date:",
            "  - Build ID:",
            "2. Scope of Release",
            "3. New Features / Changes",
            "4. Known Issues and Limitations",
            "5. Installation Instructions",
            "6. Dependencies",
            "7. Revision History",
        ],
    },
}


def transition_status(doc_id, new_status, reviewer, conn):
    """문서 상태를 전환 (유효성 검사 포함)

    DocumentStatus.TRANSITIONS에 따라 허용된 전환만 수행합니다:
        Draft -> In Review
        In Review -> Approved | Rejected
        Rejected -> Draft

    Args:
        doc_id: 문서 ID
        new_status: 새로운 상태 (DocumentStatus 값)
        reviewer: 리뷰어 이름
        conn: SQLite 연결 객체

    Returns:
        dict: 업데이트된 문서 정보

    Raises:
        ValueError: 문서가 없거나, 상태 전환이 허용되지 않는 경우
    """
    doc = DocumentModel.get_by_id(doc_id, conn=conn)
    if not doc:
        raise ValueError(f"Document with id {doc_id} not found")

    current_status = doc["status"]

    # 상태 전환 유효성 검사
    allowed = DocumentStatus.TRANSITIONS.get(current_status, [])
    if new_status not in allowed:
        raise ValueError(
            f"Cannot transition from '{current_status}' to '{new_status}'. "
            f"Allowed transitions: {allowed}"
        )

    # 업데이트 필드 준비
    update_kwargs = {"status": new_status, "conn": conn}

    if new_status == DocumentStatus.IN_REVIEW:
        update_kwargs["reviewer"] = reviewer
        update_kwargs["review_date"] = date.today().isoformat()
    elif new_status == DocumentStatus.APPROVED:
        update_kwargs["approval_date"] = date.today().isoformat()
    elif new_status == DocumentStatus.REJECTED:
        # 리젝트 시 승인일 초기화
        update_kwargs["approval_date"] = ""

    DocumentModel.update(doc_id, **update_kwargs)

    # 업데이트된 문서 반환
    return DocumentModel.get_by_id(doc_id, conn=conn)


def generate_skeleton(stage_id, template_type, project_name, oem_name, conn):
    """템플릿 유형을 기반으로 문서 스켈레톤 콘텐츠를 생성

    Args:
        stage_id: 단계 ID
        template_type: 템플릿 유형 키 (예: "SWE1_requirements_spec")
        project_name: 프로젝트 이름
        oem_name: OEM 이름
        conn: SQLite 연결 객체

    Returns:
        str: 생성된 스켈레톤 문서 텍스트

    Raises:
        ValueError: 알 수 없는 template_type이거나 stage를 찾을 수 없는 경우
    """
    # 단계 정보 조회
    stage = StageModel.get_by_id(stage_id, conn=conn)
    if not stage:
        raise ValueError(f"Stage with id {stage_id} not found")

    swe_level = stage["swe_level"]
    swe_info = SWE_STAGES.get(swe_level, {})
    stage_name = swe_info.get("name_en", swe_level)

    # 템플릿 조회
    template = _SKELETON_TEMPLATES.get(template_type)
    if not template:
        raise ValueError(
            f"Unknown template type: '{template_type}'. "
            f"Available types: {sorted(_SKELETON_TEMPLATES.keys())}"
        )

    # 스켈레톤 생성
    lines = []
    lines.append("=" * 70)
    lines.append(f"  {template['title']}")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Project:    {project_name}")
    lines.append(f"OEM:        {oem_name}")
    lines.append(f"Stage:      {swe_level} - {stage_name}")
    lines.append(f"Date:       {date.today().isoformat()}")
    lines.append(f"Status:     Draft")
    lines.append(f"Author:     [Author Name]")
    lines.append(f"Version:    0.1")
    lines.append("")
    lines.append("-" * 70)
    lines.append("")

    for section_line in template["sections"]:
        lines.append(section_line)
        # 주요 섹션(숫자로 시작) 뒤에 빈 줄 추가
        if section_line and section_line[0].isdigit() and "." in section_line[:4]:
            lines.append("")

    lines.append("")
    lines.append("-" * 70)
    lines.append(f"End of {template['title']}")
    lines.append("-" * 70)

    return "\n".join(lines)
