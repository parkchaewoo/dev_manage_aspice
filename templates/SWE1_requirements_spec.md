# Software Requirements Specification (SRS)
# 소프트웨어 요구사항 명세서

---

<!-- GUIDE: 이 문서는 시스템 요구사항으로부터 도출된 소프트웨어 요구사항을 정의합니다. -->
<!-- GUIDE: This document defines software requirements derived from system requirements. -->

| Field / 항목 | Value / 값 |
|---|---|
| Project Name / 프로젝트명 | {project_name} |
| OEM | {oem_name} |
| Document ID / 문서 ID | {document_id} |
| Version / 버전 | 0.1 |
| Date / 작성일 | {date} |
| Author / 작성자 | |
| Reviewer / 검토자 | |
| Approval / 승인자 | |
| Status / 상태 | Draft |
| ASIL Level / ASIL 등급 | |
| Classification / 기밀등급 | Confidential |

---

## Revision History / 개정 이력

| Version | Date | Author | Description / 설명 |
|---------|------|--------|-------------------|
| 0.1 | {date} | | Initial draft / 초안 작성 |
| | | | |

---

## Input Artifacts / 입력 산출물
<!-- GUIDE: 이 문서를 작성하기 위해 참조하는 상위 문서를 기록하세요 -->

| Artifact / 산출물 | Source / 출처 | Version |
|---|---|---|
| System Requirements Specification | Systems Engineering | |
| Customer Technical Specification | {oem_name} | |
| Safety Concept (ISO 26262) | Safety Team | |
| Interface Control Document | HW/SW Interface | |

## Output Artifacts / 출력 산출물

| Artifact / 산출물 | Target / 대상 | Purpose / 용도 |
|---|---|---|
| SW Requirements (this document) | SWE.2 Architecture | 아키텍처 설계 입력 |
| Requirements Traceability Matrix | SWE.6 Qualification | 적격성 시험 기준 |
| Requirements Review Report | Quality Assurance | 품질 보증 근거 |

---

## 1. Introduction / 소개

### 1.1 Purpose / 목적
<!-- GUIDE: 이 문서의 목적과 적용 범위를 기술하세요 -->
본 문서는 {project_name} 프로젝트의 소프트웨어 요구사항을 정의합니다.
This document defines the software requirements for the {project_name} project.

### 1.2 Scope / 범위
- Target ECU / 대상 ECU:
- Software Component / SW 컴포넌트:
- AUTOSAR Version:
- Development Environment:

### 1.3 Definitions and Abbreviations / 용어 정의

| Term / 용어 | Definition / 정의 |
|---|---|
| EPS | Electric Power Steering / 전동 조향 장치 |
| ASIL | Automotive Safety Integrity Level |
| ECU | Electronic Control Unit / 전자 제어 장치 |
| CAN | Controller Area Network |
| FMEA | Failure Mode and Effects Analysis |
| DTC | Diagnostic Trouble Code |
| NVM | Non-Volatile Memory |

### 1.4 References / 참조 문서

| ID | Document / 문서 | Version |
|---|---|---|
| REF-01 | ISO 26262 Road Vehicles - Functional Safety | 2018 |
| REF-02 | AUTOSAR SWS Specification | R22-11 |
| REF-03 | {oem_name} Software Development Standard | |
| REF-04 | System Requirements Specification | |

---

## 2. System Context / 시스템 컨텍스트
<!-- GUIDE: SW가 동작하는 시스템 환경, HW 인터페이스, 외부 시스템 연결을 기술하세요 -->

### 2.1 System Overview / 시스템 개요
(시스템 블록 다이어그램 또는 설명을 기술하세요)

### 2.2 Operating Conditions / 동작 조건

| Parameter / 파라미터 | Range / 범위 | Unit / 단위 |
|---|---|---|
| Supply Voltage / 공급 전압 | 9.0 ~ 16.0 | V |
| Operating Temperature / 동작 온도 | -40 ~ +85 | °C |
| CAN Baud Rate | 500 | kbps |
| Main Cycle Time / 메인 주기 | 5 | ms |

---

## 3. Functional Requirements / 기능 요구사항
<!-- GUIDE: 각 요구사항에 고유 ID를 부여하고, ASIL 등급, 우선순위, 검증 방법을 명시하세요 -->
<!-- GUIDE: 모든 요구사항은 테스트 가능해야 합니다 (Testable) -->

| ID | Requirement / 요구사항 | ASIL | Priority | Source / 출처 | Verification / 검증방법 | Acceptance Criteria / 합격 기준 |
|---|---|---|---|---|---|---|
| SWE1-REQ-001 | The SW shall read steering angle sensor input within range ±720° / SW는 조향각 센서 입력을 ±720° 범위 내에서 읽어야 한다 | B | High | SYS-REQ-101 | Test | Sensor value accuracy ±0.5° |
| SWE1-REQ-002 | The SW shall calculate assist torque output in range 0~12 Nm / SW는 보조 토크 출력을 0~12 Nm 범위에서 계산해야 한다 | B | High | SYS-REQ-102 | Test | Torque accuracy ±0.1 Nm |
| SWE1-REQ-003 | The SW shall detect sensor failure within 10ms and transition to safe state / SW는 센서 고장을 10ms 이내에 감지하고 안전 상태로 전환해야 한다 | D | Critical | SYS-REQ-201 | Test | Response time < 10ms |
| SWE1-REQ-004 | The SW shall store DTC in NVM when a fault is detected / SW는 고장 감지 시 DTC를 NVM에 저장해야 한다 | QM | Medium | SYS-REQ-301 | Test | DTC stored within 100ms |
| SWE1-REQ-005 | The SW shall communicate vehicle speed via CAN message (ID: 0x123) at 20ms cycle / SW는 CAN 메시지(ID: 0x123)로 차속을 20ms 주기로 통신해야 한다 | A | High | SYS-REQ-103 | Test | Message cycle 20ms ±2ms |
| | (요구사항을 추가하세요 / Add requirements) | | | | | |

---

## 4. Non-Functional Requirements / 비기능 요구사항

### 4.1 Performance / 성능 요구사항

| ID | Requirement / 요구사항 | Target / 목표값 | Verification |
|---|---|---|---|
| SWE1-NFR-001 | Main control loop cycle time / 메인 제어 루프 주기 | ≤ 5 ms | Test |
| SWE1-NFR-002 | Interrupt latency / 인터럽트 지연 | ≤ 50 μs | Test |
| SWE1-NFR-003 | CAN message response time / CAN 응답 시간 | ≤ 10 ms | Test |
| SWE1-NFR-004 | Boot time / 부팅 시간 | ≤ 200 ms | Test |

### 4.2 Memory / 메모리 요구사항

| Resource / 리소스 | Budget / 예산 | Target Usage / 목표 사용량 |
|---|---|---|
| RAM | 64 KB | ≤ 70% (44.8 KB) |
| ROM (Flash) | 256 KB | ≤ 80% (204.8 KB) |
| NVM (EEPROM/DataFlash) | 8 KB | ≤ 60% (4.8 KB) |
| Stack Size | 4 KB | ≤ 80% (3.2 KB) |

### 4.3 CPU Load / CPU 부하

| Condition / 조건 | Max CPU Load / 최대 부하 |
|---|---|
| Normal Operation / 정상 동작 | ≤ 60% |
| Peak Load (all features active) | ≤ 70% |
| Diagnostic Session Active | ≤ 80% |

---

## 5. Safety Requirements / 안전 요구사항
<!-- GUIDE: ISO 26262에 따른 안전 요구사항을 기술하세요 -->

### 5.1 ASIL Decomposition / ASIL 분해

| Safety Goal / 안전 목표 | ASIL | SW Safety Req | HW Safety Req |
|---|---|---|---|
| Unintended steering assist / 의도치 않은 조향 보조 방지 | D | ASIL B(SW) + ASIL B(HW) | Redundant sensor |
| Loss of steering assist / 조향 보조 상실 감지 | B | ASIL B(SW) | Monitoring circuit |

### 5.2 Safe State Definition / 안전 상태 정의

| Safe State / 안전 상태 | Description / 설명 | Entry Condition / 진입 조건 |
|---|---|---|
| SS1: Torque Zero | 보조 토크를 0으로 설정 | Critical sensor failure |
| SS2: Torque Hold | 현재 토크값 유지 후 점진적 감소 | Non-critical fault |
| SS3: Degraded Mode | 제한된 토크로 동작 | Partial system failure |

### 5.3 Fault Detection / 고장 감지

| Fault / 고장 | Detection Method / 감지 방법 | Response Time / 응답 시간 | Safe State |
|---|---|---|---|
| Steering angle sensor failure | Range check + plausibility | < 10 ms | SS1 |
| Torque sensor failure | Redundancy comparison | < 10 ms | SS1 |
| CAN communication loss | Timeout monitoring | < 100 ms | SS2 |
| CPU overload | Watchdog timer | < 50 ms | SS1 |
| NVM data corruption | CRC check | On startup | SS3 |

---

## 6. Interface Requirements / 인터페이스 요구사항

### 6.1 CAN Interface / CAN 인터페이스

| Signal / 신호 | CAN ID | Direction / 방향 | Cycle / 주기 | Data Type | Range / 범위 | Unit |
|---|---|---|---|---|---|---|
| SteeringAngle | 0x100 | Input | 10 ms | INT16 | -7200 ~ 7200 | 0.1° |
| VehicleSpeed | 0x123 | Input | 20 ms | UINT16 | 0 ~ 3000 | 0.1 km/h |
| AssistTorque | 0x200 | Output | 5 ms | INT16 | -1200 ~ 1200 | 0.01 Nm |
| SystemStatus | 0x201 | Output | 100 ms | UINT8 | 0 ~ 255 | - |
| DTCInfo | 0x7DF | Diag | On request | UINT8[] | - | - |

### 6.2 Sensor Inputs / 센서 입력

| Sensor / 센서 | Interface / 인터페이스 | Range / 범위 | Resolution / 분해능 | Accuracy / 정확도 |
|---|---|---|---|---|
| Steering Angle Sensor | SPI | ±720° | 0.1° | ±0.5° |
| Torque Sensor | ADC (12-bit) | ±10 Nm | 0.005 Nm | ±0.05 Nm |
| Motor Current Sensor | ADC (12-bit) | 0 ~ 80 A | 0.02 A | ±0.5 A |
| Temperature Sensor | ADC (10-bit) | -40 ~ 150°C | 0.5°C | ±2°C |

### 6.3 Actuator Outputs / 액추에이터 출력

| Actuator / 구동기 | Interface | Range / 범위 | Control Method |
|---|---|---|---|
| EPS Motor | PWM (20kHz) | 0 ~ 100% duty | Current control |
| Warning Lamp | GPIO | On/Off | Direct drive |
| Relay (Power) | GPIO | On/Off | Safety cutoff |

---

## 7. Diagnostic Requirements / 진단 요구사항

### 7.1 DTC List / DTC 목록

| DTC Code | Description / 설명 | Fault Type | Detection | Healing |
|---|---|---|---|---|
| C1001 | Steering angle sensor circuit failure | Permanent | 3 consecutive cycles | 40 good cycles |
| C1002 | Torque sensor signal out of range | Permanent | 2 consecutive cycles | 40 good cycles |
| C1003 | CAN communication timeout | Intermittent | 1 cycle | 10 good cycles |
| C1004 | Motor over-temperature | Intermittent | Threshold exceeded | Below threshold |
| C1005 | NVM checksum error | Permanent | On startup | After NVM restore |

---

## 8. Traceability / 추적성

### 8.1 Upstream Traceability / 상위 추적성 (System → SW)

| System Req ID | SW Req ID | Coverage / 커버리지 |
|---|---|---|
| SYS-REQ-101 | SWE1-REQ-001 | Full |
| SYS-REQ-102 | SWE1-REQ-002 | Full |
| SYS-REQ-201 | SWE1-REQ-003 | Full |
| SYS-REQ-301 | SWE1-REQ-004 | Full |
| SYS-REQ-103 | SWE1-REQ-005 | Full |

### 8.2 Downstream Traceability / 하위 추적성 (SW Req → SWE.6 Test)

| SW Req ID | SWE.6 Test Case ID | Description |
|---|---|---|
| SWE1-REQ-001 | QT-001 | Steering angle input range test |
| SWE1-REQ-002 | QT-002 | Torque output accuracy test |
| SWE1-REQ-003 | QT-003 | Safety response time test |
| SWE1-REQ-004 | QT-004 | DTC storage verification |
| SWE1-REQ-005 | QT-005 | CAN communication cycle test |

---

## 9. Review Criteria / 검토 기준
<!-- GUIDE: 이 문서의 검토 시 확인해야 할 항목들입니다 -->

| # | Criteria / 기준 | Check |
|---|---|---|
| 1 | All requirements have unique IDs / 모든 요구사항에 고유 ID 부여 | ☐ |
| 2 | All requirements are testable / 모든 요구사항이 테스트 가능 | ☐ |
| 3 | ASIL levels assigned to safety requirements / 안전 요구사항에 ASIL 등급 부여 | ☐ |
| 4 | Traceability to system requirements complete / 시스템 요구사항 추적성 완료 | ☐ |
| 5 | Interface specifications complete / 인터페이스 사양 완료 | ☐ |
| 6 | Non-functional requirements quantified / 비기능 요구사항 정량화 | ☐ |
| 7 | No ambiguous terms (should→shall) / 모호한 표현 없음 | ☐ |
| 8 | Acceptance criteria defined for each requirement / 각 요구사항에 합격 기준 정의 | ☐ |
| 9 | Safety requirements consistent with safety concept / 안전 요구사항이 안전 컨셉과 일치 | ☐ |
| 10 | DTC list complete and consistent / DTC 목록 완전하고 일관성 있음 | ☐ |

---

## 10. Review History / 검토 이력

| Date / 날짜 | Reviewer / 검토자 | Result / 결과 | Comments / 비고 |
|---|---|---|---|
| | | Approved / Rejected | |

---

## Appendix / 부록

### A. Related ASPICE Stages / 관련 ASPICE 단계

| Stage | Relationship / 관계 |
|---|---|
| SWE.1 (this) | Current document / 현재 문서 |
| SWE.2 | Architecture derives from these requirements / 아키텍처가 본 요구사항에서 도출됨 |
| SWE.6 | Qualification tests verify these requirements / 적격성 시험이 본 요구사항을 검증함 |

### B. Open Issues / 미결 사항

| ID | Issue / 이슈 | Owner | Target Date | Status |
|---|---|---|---|---|
| OI-001 | (미결 사항을 기록하세요) | | | Open |

---
*Generated by ASPICE Process Manager*
