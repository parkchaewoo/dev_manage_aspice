# Software Detailed Design Document (SDD)
# 소프트웨어 상세 설계서

---

| Field / 항목 | Value / 값 |
|---|---|
| Project Name / 프로젝트명 | {project_name} |
| OEM | {oem_name} |
| Document ID / 문서 ID | {document_id} |
| Version / 버전 | {version} |
| Date / 날짜 | {date} |
| Author / 작성자 | {author} |
| Reviewer / 검토자 | {reviewer} |
| Approver / 승인자 | {approver} |
| Status / 상태 | {status} |
| Classification / 보안등급 | {classification} |

---

## Revision History / 개정 이력

| Version / 버전 | Date / 날짜 | Author / 작성자 | Description / 설명 |
|---|---|---|---|
| {version} | {date} | {author} | {change_description} |

---

## 1. Introduction / 서론

### 1.1 Purpose / 목적

This document provides the detailed design for software units of {project_name} developed for {oem_name}. It refines the architecture defined in the SAD into implementable unit specifications.

본 문서는 {oem_name}을 위해 개발된 {project_name}의 소프트웨어 유닛 상세 설계를 제공합니다. SAD에서 정의된 아키텍처를 구현 가능한 유닛 명세로 상세화합니다.

### 1.2 Scope / 범위

{scope_description}

### 1.3 Definitions and Abbreviations / 용어 정의 및 약어

| Term / 용어 | Definition / 정의 |
|---|---|
| SDD | Software Detailed Design Document / 소프트웨어 상세 설계서 |
| SWE.3 | Software Detailed Design and Unit Construction / 소프트웨어 상세 설계 및 유닛 구현 |
| | |

### 1.4 References / 참고 문서

| ID | Document / 문서 | Version / 버전 |
|---|---|---|
| [REF-01] | Software Architecture Description (SWE.2) / SAD | |
| [REF-02] | Software Requirements Specification (SWE.1) / SRS | |
| [REF-03] | Coding Guidelines / 코딩 가이드라인 | |
| | | |

---

## 2. Design Overview / 설계 개요

### 2.1 Design Approach / 설계 접근 방식

| Approach / 접근 방식 | Description / 설명 |
|---|---|
| Design Method / 설계 방법 | Model-based (Simulink) / Hand-coded / Mixed |
| Code Generation Tool / 코드 생성 도구 | {code_gen_tool} |
| Target Language / 대상 언어 | C / C++ |
| Coding Standard / 코딩 표준 | MISRA-C:2012 |

### 2.2 Unit Decomposition Summary / 유닛 분해 요약

| Unit ID / 유닛 ID | Unit Name / 유닛명 | Parent Component / 상위 컴포넌트 | Source File / 소스 파일 | Description / 설명 |
|---|---|---|---|---|
| UNIT-001 | | SWC-001 | | |
| UNIT-002 | | SWC-001 | | |
| UNIT-003 | | SWC-002 | | |
| | | | | |

---

## 3. Detailed Unit Designs / 상세 유닛 설계

### 3.1 UNIT-001: {unit_name}

#### 3.1.1 Overview / 개요

| Attribute / 속성 | Value / 값 |
|---|---|
| Unit ID / 유닛 ID | UNIT-001 |
| Unit Name / 유닛명 | {unit_name} |
| Parent Component / 상위 컴포넌트 | {parent_component_id} |
| Source File / 소스 파일 | {source_file} |
| Header File / 헤더 파일 | {header_file} |
| ASIL | {asil_level} |
| Description / 설명 | {unit_description} |

#### 3.1.2 Interface / 인터페이스

**Input Parameters / 입력 매개변수:**

| Name / 이름 | Type / 유형 | Range / 범위 | Unit / 단위 | Description / 설명 |
|---|---|---|---|---|
| {param_name} | {data_type} | {min} ~ {max} | | |
| | | | | |

**Output Parameters / 출력 매개변수:**

| Name / 이름 | Type / 유형 | Range / 범위 | Unit / 단위 | Description / 설명 |
|---|---|---|---|---|
| {param_name} | {data_type} | {min} ~ {max} | | |
| | | | | |

**Global Variables Used / 사용된 전역 변수:**

| Name / 이름 | Type / 유형 | Access / 접근 | Description / 설명 |
|---|---|---|---|
| | | Read/Write | |
| | | | |

#### 3.1.3 Algorithm / 알고리즘

{algorithm_description}

```
Pseudocode / 의사코드:
-----------------------
FUNCTION {function_name}(inputs)
    // Step 1: {step_description}
    // Step 2: {step_description}
    RETURN output
END FUNCTION
```

#### 3.1.4 State Machine (if applicable) / 상태 머신 (해당 시)

| State / 상태 | Entry Action / 진입 동작 | During Action / 수행 동작 | Exit Action / 종료 동작 | Transitions / 전이 |
|---|---|---|---|---|
| | | | | |

#### 3.1.5 Error Handling / 에러 처리

| Error Condition / 에러 조건 | Detection / 검출 | Reaction / 반응 | DTC (if applicable) |
|---|---|---|---|
| | | | |

#### 3.1.6 Calibration Parameters / 캘리브레이션 매개변수

| Name / 이름 | Type / 유형 | Default / 기본값 | Range / 범위 | Description / 설명 |
|---|---|---|---|---|
| | | | | |

---

## 4. Data Structures / 데이터 구조

### 4.1 Type Definitions / 유형 정의

| Type Name / 유형명 | Base Type / 기본 유형 | Size (Bytes) | Description / 설명 |
|---|---|---|---|
| | | | |

### 4.2 Enumerations / 열거형

| Enum Name / 열거형명 | Values / 값 | Description / 설명 |
|---|---|---|
| | | |

### 4.3 Structures / 구조체

| Struct Name / 구조체명 | Members / 멤버 | Size (Bytes) | Description / 설명 |
|---|---|---|---|
| | | | |

---

## 5. NVM Data / NVM 데이터

| Block ID / 블록 ID | Name / 이름 | Size (Bytes) | Default / 기본값 | Write Condition / 쓰기 조건 | Description / 설명 |
|---|---|---|---|---|---|
| | | | | | |

---

## 6. Static Analysis and Coding Compliance / 정적 분석 및 코딩 준수

### 6.1 MISRA-C Compliance / MISRA-C 준수

| Rule Category / 규칙 분류 | Total Rules / 전체 규칙 | Compliant / 준수 | Deviations / 편차 | Justification / 근거 |
|---|---|---|---|---|
| Mandatory / 필수 | | | | |
| Required / 요구 | | | | |
| Advisory / 권고 | | | | |

### 6.2 Static Analysis Summary / 정적 분석 요약

| Tool / 도구 | Critical / 치명적 | Major / 주요 | Minor / 경미 | Info / 정보 |
|---|---|---|---|---|
| {analysis_tool} | | | | |

---

## 7. Traceability / 추적성

### 7.1 Upstream Traceability from SWE.2 / SWE.2 상위 추적성

Each unit shall trace back to at least one architecture component (SWE.2).

각 유닛은 최소 하나의 아키텍처 컴포넌트 (SWE.2)로 역추적되어야 합니다.

| Component ID / 컴포넌트 ID | Unit ID / 유닛 ID | Coverage / 커버리지 |
|---|---|---|
| SWC-001 | UNIT-001 | |
| SWC-001 | UNIT-002 | |
| | | |

### 7.2 Upstream Traceability from SWE.1 / SWE.1 상위 추적성

| SW Req ID / SW 요구사항 ID | Unit ID / 유닛 ID | Function / 함수 |
|---|---|---|
| SWR-F-001 | UNIT-001 | |
| | | |

### 7.3 Downstream Traceability to SWE.4 / SWE.4 하위 추적성

Each unit shall be verified by at least one unit test case (SWE.4).

각 유닛은 최소 하나의 유닛 테스트 케이스 (SWE.4)로 검증되어야 합니다.

| Unit ID / 유닛 ID | Unit Test ID / 유닛 테스트 ID | Result / 결과 |
|---|---|---|
| UNIT-001 | | |
| | | |

---

## 8. Appendix / 부록

### 8.1 Related ASPICE Stages / 관련 ASPICE 단계

| Stage / 단계 | Relationship / 관계 | Document / 문서 |
|---|---|---|
| SWE.1 | Requirements flow to unit level / 요구사항이 유닛 레벨까지 흐름 | SRS |
| SWE.2 | Units refine architecture components / 유닛이 아키텍처 컴포넌트를 상세화 | SAD |
| SWE.4 | Units are verified by unit tests / 유닛이 유닛 테스트로 검증됨 | UTR |

### 8.2 Code Review Records / 코드 리뷰 기록

| Review ID / 리뷰 ID | Date / 날짜 | Reviewer / 검토자 | Findings / 발견사항 | Status / 상태 |
|---|---|---|---|---|
| | | | | |

### 8.3 Open Issues / 미결 사항

| ID | Description / 설명 | Owner / 담당자 | Due Date / 기한 |
|---|---|---|---|
| | | | |
