"""ASPICE 가이드 서비스 - 한국어/영어 초보자 가이드"""

STAGE_GUIDES = {
    "SWE.1": {
        "ko": {
            "title": "소프트웨어 요구사항 분석",
            "what": "시스템 요구사항으로부터 소프트웨어 요구사항을 도출하고 문서화합니다. "
                    "기능 요구사항, 비기능 요구사항(성능, 안전, 보안 등)을 모두 포함해야 합니다.",
            "why": "V-Model의 시작점입니다. 여기서 정의한 요구사항이 SWE.6(적격성 시험)에서 검증됩니다. "
                   "요구사항이 명확하지 않으면 이후 모든 단계에 영향을 미칩니다.",
            "documents": [
                "소프트웨어 요구사항 명세서 (SRS)",
                "요구사항 검토 보고서",
                "요구사항 추적 매트릭스"
            ],
            "tips": [
                "모든 요구사항에 고유 ID를 부여하세요 (예: SWE1-REQ-001)",
                "각 요구사항은 테스트 가능해야 합니다",
                "시스템 요구사항과의 추적성을 반드시 기록하세요",
                "우선순위를 명확히 구분하세요 (High/Medium/Low)",
                "예시: EPS 시스템의 경우 '조향각 센서 입력값 범위: ±720°' 같은 구체적 수치를 포함"
            ],
            "next_step": "요구사항 작성 및 검토 완료 후 → SWE.2 아키텍처 설계로 진행",
            "v_model_pair": "SWE.6 (적격성 시험) - 여기서 정의한 요구사항을 SWE.6에서 시험합니다"
        },
        "en": {
            "title": "Software Requirements Analysis",
            "what": "Derive and document software requirements from system requirements. "
                    "Include both functional and non-functional requirements (performance, safety, security).",
            "why": "This is the starting point of the V-Model. Requirements defined here will be verified "
                   "in SWE.6 (Qualification Test). Unclear requirements affect all subsequent stages.",
            "documents": [
                "Software Requirements Specification (SRS)",
                "Requirements Review Report",
                "Requirements Traceability Matrix"
            ],
            "tips": [
                "Assign unique IDs to all requirements (e.g., SWE1-REQ-001)",
                "Each requirement must be testable",
                "Always record traceability to system requirements",
                "Clearly distinguish priority levels (High/Medium/Low)",
                "Example: For EPS system, include specific values like 'Steering angle sensor input range: ±720°'"
            ],
            "next_step": "After requirements writing and review → proceed to SWE.2 Architectural Design",
            "v_model_pair": "SWE.6 (Qualification Test) - Requirements defined here are tested in SWE.6"
        }
    },
    "SWE.2": {
        "ko": {
            "title": "소프트웨어 아키텍처 설계",
            "what": "SWE.1의 요구사항을 기반으로 소프트웨어의 전체 구조를 설계합니다. "
                    "컴포넌트 분할, 인터페이스 정의, 데이터 흐름을 포함합니다.",
            "why": "아키텍처는 소프트웨어의 뼈대입니다. SWE.5(통합 시험)에서 이 설계가 올바른지 검증합니다. "
                   "잘못된 아키텍처는 나중에 수정하기 매우 어렵습니다.",
            "documents": [
                "소프트웨어 아키텍처 설계서 (SAD)",
                "인터페이스 설계서",
                "아키텍처 검토 보고서"
            ],
            "tips": [
                "AUTOSAR 아키텍처 패턴을 참고하세요",
                "각 컴포넌트의 책임을 명확히 정의하세요",
                "인터페이스(입력/출력)를 상세히 기술하세요",
                "리소스(메모리, CPU) 제약사항을 고려하세요",
                "예시: 조향 시스템의 경우 센서 입력→제어 로직→액추에이터 출력 구조"
            ],
            "next_step": "아키텍처 설계 및 검토 완료 후 → SWE.3 상세 설계로 진행",
            "v_model_pair": "SWE.5 (통합 시험) - 여기서 설계한 아키텍처를 SWE.5에서 통합 시험합니다"
        },
        "en": {
            "title": "Software Architectural Design",
            "what": "Design the overall software structure based on SWE.1 requirements. "
                    "Include component decomposition, interface definitions, and data flows.",
            "why": "Architecture is the backbone of software. SWE.5 (Integration Test) verifies this design. "
                   "Poor architecture is very difficult to fix later.",
            "documents": [
                "Software Architecture Document (SAD)",
                "Interface Design Document",
                "Architecture Review Report"
            ],
            "tips": [
                "Reference AUTOSAR architecture patterns",
                "Clearly define each component's responsibilities",
                "Describe interfaces (input/output) in detail",
                "Consider resource constraints (memory, CPU)",
                "Example: For steering system - Sensor Input → Control Logic → Actuator Output structure"
            ],
            "next_step": "After architecture design and review → proceed to SWE.3 Detailed Design",
            "v_model_pair": "SWE.5 (Integration Test) - Architecture designed here is integration-tested in SWE.5"
        }
    },
    "SWE.3": {
        "ko": {
            "title": "소프트웨어 상세 설계 및 단위 구현",
            "what": "SWE.2의 아키텍처를 기반으로 각 컴포넌트의 상세 설계를 작성하고 코드를 구현합니다. "
                    "알고리즘, 데이터 구조, 함수 인터페이스를 정의합니다.",
            "why": "V-Model의 최하단으로, 실제 코드가 작성되는 단계입니다. "
                   "SWE.4(단위 검증)에서 이 단위들이 올바른지 검증합니다.",
            "documents": [
                "상세 설계서 (SDD)",
                "소스 코드",
                "코딩 가이드라인 준수 보고서"
            ],
            "tips": [
                "MISRA-C 등 코딩 표준을 준수하세요",
                "함수별 입출력 사양을 명확히 정의하세요",
                "단위 테스트 가능한 구조로 설계하세요",
                "정적 분석 도구(Polyspace, QAC 등)를 활용하세요",
                "예시: PID 제어 알고리즘의 경우 P/I/D 각 항의 계산 로직을 상세히 기술"
            ],
            "next_step": "코드 구현 완료 후 → SWE.4 단위 검증으로 진행",
            "v_model_pair": "SWE.4 (단위 검증) - 여기서 구현한 단위를 SWE.4에서 검증합니다"
        },
        "en": {
            "title": "Software Detailed Design and Unit Construction",
            "what": "Create detailed design for each component from SWE.2 architecture and implement the code. "
                    "Define algorithms, data structures, and function interfaces.",
            "why": "This is the bottom of the V-Model where actual code is written. "
                   "SWE.4 (Unit Verification) verifies these units are correct.",
            "documents": [
                "Software Detailed Design Document (SDD)",
                "Source Code",
                "Coding Guideline Compliance Report"
            ],
            "tips": [
                "Follow coding standards like MISRA-C",
                "Clearly define input/output specs per function",
                "Design for unit testability",
                "Use static analysis tools (Polyspace, QAC, etc.)",
                "Example: For PID control, describe P/I/D calculation logic in detail"
            ],
            "next_step": "After code implementation → proceed to SWE.4 Unit Verification",
            "v_model_pair": "SWE.4 (Unit Verification) - Units implemented here are verified in SWE.4"
        }
    },
    "SWE.4": {
        "ko": {
            "title": "소프트웨어 단위 검증",
            "what": "SWE.3에서 구현한 각 소프트웨어 단위(함수, 모듈)가 상세 설계에 맞게 "
                    "올바르게 동작하는지 검증합니다. 단위 테스트를 수행합니다.",
            "why": "개별 단위가 올바르지 않으면 통합 시 더 큰 문제가 발생합니다. "
                   "이 단계에서 버그를 조기에 발견하면 수정 비용이 적습니다.",
            "documents": [
                "단위 시험 계획서",
                "단위 시험 보고서",
                "코드 커버리지 보고서"
            ],
            "tips": [
                "구문 커버리지(Statement), 분기 커버리지(Branch), MC/DC 커버리지 목표를 설정하세요",
                "경계값, 예외 상황을 반드시 테스트하세요",
                "테스트 프레임워크(Google Test, Unity 등)를 활용하세요",
                "정적 분석 결과도 함께 검토하세요",
                "예시: 조향각 계산 함수에 대해 정상 범위, 경계값, 오버플로우 케이스 테스트"
            ],
            "next_step": "단위 검증 완료 후 → SWE.5 통합 시험으로 진행",
            "v_model_pair": "SWE.3 (상세 설계) - SWE.3의 상세 설계에 대해 검증합니다"
        },
        "en": {
            "title": "Software Unit Verification",
            "what": "Verify that each software unit (function, module) from SWE.3 works correctly "
                    "according to the detailed design. Perform unit testing.",
            "why": "If individual units are not correct, larger problems occur during integration. "
                   "Finding bugs at this stage minimizes fix costs.",
            "documents": [
                "Unit Test Plan",
                "Unit Test Report",
                "Code Coverage Report"
            ],
            "tips": [
                "Set coverage targets: Statement, Branch, MC/DC",
                "Always test boundary values and exception cases",
                "Use test frameworks (Google Test, Unity, etc.)",
                "Also review static analysis results",
                "Example: Test steering angle calculation with normal range, boundary, overflow cases"
            ],
            "next_step": "After unit verification → proceed to SWE.5 Integration Test",
            "v_model_pair": "SWE.3 (Detailed Design) - Verifies the detailed design from SWE.3"
        }
    },
    "SWE.5": {
        "ko": {
            "title": "소프트웨어 통합 및 통합 시험",
            "what": "검증된 단위들을 통합하고, 통합된 소프트웨어가 SWE.2의 아키텍처 설계에 맞게 "
                    "동작하는지 시험합니다. 컴포넌트 간 인터페이스를 검증합니다.",
            "why": "개별 단위가 올바르더라도 통합 시 인터페이스 불일치, 타이밍 문제 등이 발생할 수 있습니다. "
                   "SWE.2의 아키텍처 설계가 올바르게 구현되었는지 확인합니다.",
            "documents": [
                "통합 시험 계획서",
                "통합 시험 보고서",
                "통합 전략 문서"
            ],
            "tips": [
                "점진적 통합(incremental integration) 전략을 사용하세요",
                "컴포넌트 간 인터페이스를 집중적으로 테스트하세요",
                "실제 타겟 환경에서 테스트하세요 (HIL 시뮬레이터 활용)",
                "타이밍, 리소스 사용량도 확인하세요",
                "예시: 조향 센서 모듈 + 제어 로직 모듈 통합 후 데이터 전달 정확성 검증"
            ],
            "next_step": "통합 시험 완료 후 → SWE.6 적격성 시험으로 진행",
            "v_model_pair": "SWE.2 (아키텍처 설계) - SWE.2의 아키텍처에 대해 통합 시험합니다"
        },
        "en": {
            "title": "Software Integration and Integration Test",
            "what": "Integrate verified units and test that the integrated software works according to "
                    "SWE.2 architecture design. Verify interfaces between components.",
            "why": "Even if individual units are correct, interface mismatches and timing issues can occur "
                   "during integration. Confirms SWE.2 architecture is correctly implemented.",
            "documents": [
                "Integration Test Plan",
                "Integration Test Report",
                "Integration Strategy Document"
            ],
            "tips": [
                "Use incremental integration strategy",
                "Focus testing on component interfaces",
                "Test on actual target environment (use HIL simulator)",
                "Check timing and resource usage",
                "Example: Integrate steering sensor + control logic modules, verify data transfer accuracy"
            ],
            "next_step": "After integration test → proceed to SWE.6 Qualification Test",
            "v_model_pair": "SWE.2 (Architectural Design) - Integration tests against SWE.2 architecture"
        }
    },
    "SWE.6": {
        "ko": {
            "title": "소프트웨어 적격성 시험",
            "what": "통합된 소프트웨어가 SWE.1의 소프트웨어 요구사항을 충족하는지 최종 시험합니다. "
                    "전체 시스템 레벨에서의 기능 및 비기능 시험을 수행합니다.",
            "why": "V-Model의 최상단 우측으로, SWE.1에서 정의한 모든 요구사항이 충족되는지 최종 확인합니다. "
                   "이 단계를 통과해야 소프트웨어가 릴리스 가능합니다.",
            "documents": [
                "적격성 시험 계획서",
                "적격성 시험 보고서",
                "요구사항 커버리지 보고서"
            ],
            "tips": [
                "SWE.1의 모든 요구사항에 대한 시험 항목이 있는지 확인하세요 (100% 커버리지)",
                "실제 운영 환경과 동일한 조건에서 테스트하세요",
                "비기능 요구사항(성능, 안전)도 빠짐없이 시험하세요",
                "회귀 테스트를 반드시 수행하세요",
                "예시: 조향 시스템의 경우 정상 주행, 긴급 조향, 센서 고장 시나리오 등 모든 사용 케이스 시험"
            ],
            "next_step": "적격성 시험 통과 → 소프트웨어 릴리스 준비",
            "v_model_pair": "SWE.1 (요구사항 분석) - SWE.1의 요구사항에 대해 적격성 시험합니다"
        },
        "en": {
            "title": "Software Qualification Test",
            "what": "Final test that integrated software meets SWE.1 software requirements. "
                    "Perform functional and non-functional testing at the system level.",
            "why": "Top-right of V-Model. Final confirmation that all SWE.1 requirements are satisfied. "
                   "Software can only be released after passing this stage.",
            "documents": [
                "Qualification Test Plan",
                "Qualification Test Report",
                "Requirements Coverage Report"
            ],
            "tips": [
                "Verify test cases exist for ALL SWE.1 requirements (100% coverage)",
                "Test under conditions identical to actual operating environment",
                "Don't miss non-functional requirements (performance, safety)",
                "Always perform regression testing",
                "Example: For steering system, test all use cases - normal driving, emergency steering, sensor failure scenarios"
            ],
            "next_step": "After qualification test pass → prepare for software release",
            "v_model_pair": "SWE.1 (Requirements Analysis) - Qualification test against SWE.1 requirements"
        }
    },
}


def get_guide(swe_level, lang="ko"):
    """특정 단계의 가이드 반환"""
    return STAGE_GUIDES.get(swe_level, {}).get(lang, {})


def get_all_stages():
    """모든 단계 목록 반환"""
    return list(STAGE_GUIDES.keys())
