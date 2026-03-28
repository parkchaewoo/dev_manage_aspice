# Software Requirements Specification (SRS)
# 소프트웨어 요구사항 명세서

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

This document specifies the software requirements for {project_name} developed for {oem_name}.

본 문서는 {oem_name}을 위해 개발된 {project_name}의 소프트웨어 요구사항을 명세합니다.

### 1.2 Scope / 범위

{scope_description}

### 1.3 Definitions and Abbreviations / 용어 정의 및 약어

| Term / 용어 | Definition / 정의 |
|---|---|
| SRS | Software Requirements Specification / 소프트웨어 요구사항 명세서 |
| SWE.1 | Software Requirements Analysis / 소프트웨어 요구사항 분석 |
| | |

### 1.4 References / 참고 문서

| ID | Document / 문서 | Version / 버전 |
|---|---|---|
| [REF-01] | System Requirements Specification / 시스템 요구사항 명세서 | |
| [REF-02] | {oem_name} Development Standards / 개발 표준 | |
| | | |

---

## 2. Overall Description / 전체 개요

### 2.1 Product Perspective / 제품 개관

{product_perspective}

### 2.2 System Context / 시스템 컨텍스트

{system_context_description}

### 2.3 Constraints / 제약 조건

| ID | Constraint / 제약 조건 | Source / 출처 |
|---|---|---|
| CON-001 | | |
| | | |

---

## 3. Functional Requirements / 기능 요구사항

### 3.1 Functional Requirement Summary / 기능 요구사항 요약

| Req ID / 요구사항 ID | Title / 제목 | Priority / 우선순위 | ASIL | Source / 출처 |
|---|---|---|---|---|
| SWR-F-001 | | | | |
| | | | | |

### 3.2 Detailed Functional Requirements / 상세 기능 요구사항

#### SWR-F-001: {requirement_title}

| Attribute / 속성 | Value / 값 |
|---|---|
| ID | SWR-F-001 |
| Title / 제목 | {requirement_title} |
| Description / 설명 | {requirement_description} |
| Rationale / 근거 | |
| Source / 출처 | {source_system_requirement_id} |
| Priority / 우선순위 | {priority} |
| ASIL | {asil_level} |
| Verification Method / 검증 방법 | {verification_method} |
| Acceptance Criteria / 인수 기준 | |

---

## 4. Non-Functional Requirements / 비기능 요구사항

### 4.1 Performance Requirements / 성능 요구사항

| Req ID / 요구사항 ID | Description / 설명 | Target Value / 목표값 | Unit / 단위 |
|---|---|---|---|
| SWR-P-001 | | | |
| | | | |

### 4.2 Memory Requirements / 메모리 요구사항

| Resource / 리소스 | Budget / 예산 | Unit / 단위 |
|---|---|---|
| ROM | | KB |
| RAM | | KB |
| EEPROM/NVM | | KB |
| Stack | | Bytes |

### 4.3 Timing Requirements / 타이밍 요구사항

| Req ID / 요구사항 ID | Function / 기능 | Max Time / 최대 시간 | Unit / 단위 |
|---|---|---|---|
| SWR-T-001 | | | ms |
| | | | |

### 4.4 Safety Requirements / 안전 요구사항

| Req ID / 요구사항 ID | Description / 설명 | ASIL | Safety Mechanism / 안전 메커니즘 |
|---|---|---|---|
| SWR-S-001 | | | |
| | | | |

### 4.5 Diagnostic Requirements / 진단 요구사항

| Req ID / 요구사항 ID | DTC | Description / 설명 | Detection Condition / 검출 조건 |
|---|---|---|---|
| SWR-D-001 | | | |
| | | | |

---

## 5. Interface Requirements / 인터페이스 요구사항

### 5.1 Communication Interfaces / 통신 인터페이스

| Signal / 신호 | Direction / 방향 | Protocol / 프로토콜 | Cycle Time / 주기 | Description / 설명 |
|---|---|---|---|---|
| | TX/RX | CAN/LIN/ETH | | |
| | | | | |

### 5.2 Hardware Interfaces / 하드웨어 인터페이스

| Interface / 인터페이스 | Type / 유형 | Description / 설명 |
|---|---|---|
| | ADC/PWM/DIO | |
| | | |

---

## 6. Traceability / 추적성

### 6.1 Upstream Traceability (System -> SW Requirements) / 상위 추적성

| System Req ID / 시스템 요구사항 ID | SW Req ID / SW 요구사항 ID | Coverage / 커버리지 |
|---|---|---|
| SYS-001 | SWR-F-001 | |
| | | |

### 6.2 Downstream Traceability to SWE.2 / SWE.2 하위 추적성

This document's requirements are traced forward to the Software Architecture Description (SWE.2).

본 문서의 요구사항은 소프트웨어 아키텍처 설계서 (SWE.2)로 전방 추적됩니다.

| SW Req ID / SW 요구사항 ID | Architecture Element / 아키텍처 요소 | Link Status / 연결 상태 |
|---|---|---|
| SWR-F-001 | | |
| | | |

### 6.3 Traceability to SWE.6 (Qualification Test) / SWE.6 추적성 (적격성 테스트)

Each requirement in this document shall be validated by at least one qualification test case (SWE.6).

본 문서의 각 요구사항은 최소 하나의 적격성 테스트 케이스 (SWE.6)로 검증되어야 합니다.

| SW Req ID / SW 요구사항 ID | Qualification Test ID / 적격성 테스트 ID | Result / 결과 |
|---|---|---|
| SWR-F-001 | | |
| | | |

---

## 7. Appendix / 부록

### 7.1 Related ASPICE Stages / 관련 ASPICE 단계

| Stage / 단계 | Relationship / 관계 | Document / 문서 |
|---|---|---|
| SWE.2 | Requirements are designed by architecture / 요구사항이 아키텍처로 설계됨 | SAD |
| SWE.3 | Requirements flow down to detailed design / 요구사항이 상세 설계로 흐름 | SDD |
| SWE.6 | Requirements are validated by qualification tests / 요구사항이 적격성 테스트로 검증됨 | QTR |

### 7.2 Open Issues / 미결 사항

| ID | Description / 설명 | Owner / 담당자 | Due Date / 기한 |
|---|---|---|---|
| | | | |
