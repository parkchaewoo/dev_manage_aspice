# Software Architecture Description (SAD)
# 소프트웨어 아키텍처 설계서

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

This document describes the software architecture for {project_name} developed for {oem_name}.

본 문서는 {oem_name}을 위해 개발된 {project_name}의 소프트웨어 아키텍처를 설명합니다.

### 1.2 Scope / 범위

{scope_description}

### 1.3 Definitions and Abbreviations / 용어 정의 및 약어

| Term / 용어 | Definition / 정의 |
|---|---|
| SAD | Software Architecture Description / 소프트웨어 아키텍처 설계서 |
| SWE.2 | Software Architectural Design / 소프트웨어 아키텍처 설계 |
| SWC | Software Component / 소프트웨어 컴포넌트 |
| BSW | Basic Software / 기본 소프트웨어 |
| ASW | Application Software / 응용 소프트웨어 |
| RTE | Runtime Environment / 런타임 환경 |
| | |

### 1.4 References / 참고 문서

| ID | Document / 문서 | Version / 버전 |
|---|---|---|
| [REF-01] | Software Requirements Specification (SWE.1) / SRS | |
| [REF-02] | System Architecture Description | |
| [REF-03] | {oem_name} Platform Standard / 플랫폼 표준 | |
| | | |

---

## 2. Architecture Overview / 아키텍처 개요

### 2.1 Architecture Goals and Constraints / 아키텍처 목표 및 제약 조건

| Goal / 목표 | Description / 설명 |
|---|---|
| Modularity / 모듈성 | |
| Reusability / 재사용성 | |
| Safety / 안전성 | |
| Performance / 성능 | |

### 2.2 High-Level Architecture Diagram / 상위 아키텍처 다이어그램

{architecture_diagram_reference}

### 2.3 Architecture Patterns / 아키텍처 패턴

| Pattern / 패턴 | Application / 적용 영역 | Rationale / 근거 |
|---|---|---|
| Layered Architecture / 계층 아키텍처 | | |
| | | |

---

## 3. Software Component Decomposition / 소프트웨어 컴포넌트 분해

### 3.1 Component Overview / 컴포넌트 개요

| Component ID / 컴포넌트 ID | Name / 이름 | Layer / 계층 | Description / 설명 | ASIL |
|---|---|---|---|---|
| SWC-001 | | ASW/BSW | | |
| SWC-002 | | ASW/BSW | | |
| | | | | |

### 3.2 Component Descriptions / 컴포넌트 상세 설명

#### SWC-001: {component_name}

| Attribute / 속성 | Value / 값 |
|---|---|
| Component ID / 컴포넌트 ID | SWC-001 |
| Name / 이름 | {component_name} |
| Layer / 계층 | {layer} |
| Description / 설명 | {component_description} |
| Responsibility / 책임 | |
| Source Requirements / 원본 요구사항 | {source_requirement_ids} |
| ASIL | {asil_level} |
| Scheduling / 스케줄링 | {task_cycle_time} |

---

## 4. Interface Specification / 인터페이스 명세

### 4.1 Internal Interfaces / 내부 인터페이스

| Interface ID / 인터페이스 ID | Source / 소스 | Target / 대상 | Data / 데이터 | Type / 유형 | Description / 설명 |
|---|---|---|---|---|---|
| IF-INT-001 | SWC-001 | SWC-002 | | Sender-Receiver / Client-Server | |
| | | | | | |

### 4.2 External Interfaces / 외부 인터페이스

| Interface ID / 인터페이스 ID | Protocol / 프로토콜 | Direction / 방향 | Signal/Service / 신호/서비스 | Cycle / 주기 |
|---|---|---|---|---|
| IF-EXT-001 | CAN/LIN/ETH | TX/RX | | |
| | | | | |

### 4.3 Hardware Abstraction Interfaces / 하드웨어 추상화 인터페이스

| Interface ID / 인터페이스 ID | HW Resource / HW 리소스 | Access Type / 접근 유형 | Description / 설명 |
|---|---|---|---|
| IF-HW-001 | | ADC/PWM/DIO/SPI | |
| | | | |

---

## 5. Dynamic Behavior / 동적 동작

### 5.1 Task Architecture / 태스크 아키텍처

| Task Name / 태스크명 | Cycle Time / 주기 | Priority / 우선순위 | Components / 컴포넌트 | Max Execution Time / 최대 실행 시간 |
|---|---|---|---|---|
| Task_1ms | 1 ms | | | |
| Task_5ms | 5 ms | | | |
| Task_10ms | 10 ms | | | |
| Task_100ms | 100 ms | | | |
| | | | | |

### 5.2 State Machine / 상태 머신

{state_machine_diagram_reference}

| State / 상태 | Description / 설명 | Entry Condition / 진입 조건 | Exit Condition / 종료 조건 |
|---|---|---|---|
| INIT | Initialization / 초기화 | Power-on | |
| RUNNING | Normal Operation / 정상 동작 | | |
| ERROR | Error State / 에러 상태 | | |
| | | | |

### 5.3 Sequence Diagrams / 시퀀스 다이어그램

{sequence_diagram_reference}

---

## 6. Resource Budgets / 리소스 예산

### 6.1 Memory Budget / 메모리 예산

| Component / 컴포넌트 | ROM (KB) | RAM (KB) | NVM (KB) | Stack (Bytes) |
|---|---|---|---|---|
| SWC-001 | | | | |
| SWC-002 | | | | |
| BSW | | | | |
| **Total / 합계** | | | | |
| **Budget / 예산** | | | | |
| **Margin / 여유 (%)** | | | | |

### 6.2 CPU Budget / CPU 예산

| Task / 태스크 | Avg Load (%) / 평균 부하 | Max Load (%) / 최대 부하 | Budget (%) / 예산 |
|---|---|---|---|
| Task_1ms | | | |
| Task_10ms | | | |
| **Total / 합계** | | | |

---

## 7. Safety Architecture / 안전 아키텍처

### 7.1 Safety Decomposition / 안전 분해

| Component / 컴포넌트 | ASIL | Safety Mechanism / 안전 메커니즘 | Fault Reaction / 고장 반응 |
|---|---|---|---|
| | | | |

### 7.2 Freedom from Interference / 간섭으로부터의 자유

| Partitioning Method / 파티셔닝 방법 | Scope / 범위 | Description / 설명 |
|---|---|---|
| Memory Protection / 메모리 보호 | | |
| Timing Protection / 타이밍 보호 | | |
| | | |

---

## 8. Traceability / 추적성

### 8.1 Upstream Traceability from SWE.1 / SWE.1 상위 추적성

Each architecture element shall trace back to at least one software requirement (SWE.1).

각 아키텍처 요소는 최소 하나의 소프트웨어 요구사항 (SWE.1)으로 역추적되어야 합니다.

| SW Req ID / SW 요구사항 ID | Component ID / 컴포넌트 ID | Coverage / 커버리지 |
|---|---|---|
| SWR-F-001 | SWC-001 | |
| | | |

### 8.2 Downstream Traceability to SWE.3 / SWE.3 하위 추적성

Architecture components are refined in the Detailed Design (SWE.3).

아키텍처 컴포넌트는 상세 설계 (SWE.3)에서 상세화됩니다.

| Component ID / 컴포넌트 ID | Detailed Design Unit / 상세 설계 유닛 | Link Status / 연결 상태 |
|---|---|---|
| SWC-001 | | |
| | | |

### 8.3 Traceability to SWE.5 (Integration Test) / SWE.5 추적성 (통합 테스트)

Each architecture interface shall be verified by at least one integration test case (SWE.5).

각 아키텍처 인터페이스는 최소 하나의 통합 테스트 케이스 (SWE.5)로 검증되어야 합니다.

| Interface ID / 인터페이스 ID | Integration Test ID / 통합 테스트 ID | Result / 결과 |
|---|---|---|
| IF-INT-001 | | |
| | | |

---

## 9. Appendix / 부록

### 9.1 Related ASPICE Stages / 관련 ASPICE 단계

| Stage / 단계 | Relationship / 관계 | Document / 문서 |
|---|---|---|
| SWE.1 | Architecture is derived from requirements / 아키텍처는 요구사항에서 도출됨 | SRS |
| SWE.3 | Architecture is detailed by unit design / 아키텍처가 유닛 설계로 상세화됨 | SDD |
| SWE.5 | Architecture interfaces verified by integration test / 아키텍처 인터페이스가 통합 테스트로 검증됨 | ITR |

### 9.2 Architecture Decision Records / 아키텍처 결정 기록

| ID | Decision / 결정 | Rationale / 근거 | Date / 날짜 | Status / 상태 |
|---|---|---|---|---|
| ADR-001 | | | | |
| | | | | |

### 9.3 Open Issues / 미결 사항

| ID | Description / 설명 | Owner / 담당자 | Due Date / 기한 |
|---|---|---|---|
| | | | |
