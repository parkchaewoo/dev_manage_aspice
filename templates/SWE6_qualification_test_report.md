# Software Qualification Test Report (SQTR)
# 소프트웨어 적격성 시험 보고서

---
<!-- GUIDE: SWE.1 요구사항에 대해 통합된 소프트웨어를 최종 시험하는 보고서입니다 -->
<!-- GUIDE: V-Model 최상단 우측: 이 시험을 통과해야 소프트웨어 릴리스 가능 -->

| Field / 항목 | Value / 값 |
|---|---|
| Project Name | {project_name} |
| OEM | {oem_name} |
| Document ID | {document_id} |
| Version | 0.1 |
| Date | {date} |
| Author | |
| Reviewer | |
| Status | Draft |

## Input Artifacts / 입력 산출물
| Artifact | Source |
|---|---|
| Software Requirements Specification (SWE.1) | SWE.1 |
| Integrated SW (SWE.5 output) | SWE.5 |
| Integration Test Report (SWE.5) | SWE.5 |

## Output Artifacts / 출력 산출물
| Artifact | Target |
|---|---|
| Qualification Test Report (this) | Release / 릴리스 |
| SW Release Package | Production |

---

## 1. Test Scope and Objectives / 시험 범위 및 목표
<!-- GUIDE: V-Model 쌍: SWE.1(요구사항) ↔ SWE.6(적격성시험) -->
본 문서는 SWE.1에서 정의한 모든 소프트웨어 요구사항이 충족되는지 최종 검증합니다.

**Objectives / 목표:**
- 100% requirements coverage (모든 요구사항에 대한 시험 항목 존재)
- All functional/non-functional requirements verified
- Safety requirements (ASIL) verified
- System-level behavior validated

---

## 2. Test Environment / 시험 환경

| Item | Description |
|---|---|
| Platform | HIL + Target ECU (production-equivalent) |
| HIL Simulator | dSPACE / ETAS LABCAR |
| CAN Simulation | Vector CANoe + Plant Model |
| Test Automation | Python + CANape |
| Environmental | Temperature chamber (-40°C ~ +85°C) |
| SW Version | |
| HW Version | |

---

## 3. Requirements Coverage Matrix / 요구사항 커버리지 매트릭스
<!-- GUIDE: SWE.1의 모든 요구사항에 대한 시험 항목과 결과를 매핑하세요 -->
<!-- GUIDE: 100% 커버리지가 목표입니다. 빈 행이 있으면 안 됩니다 -->

| SWE.1 Req ID | Requirement / 요구사항 | QT Test ID | Test Method | Result | Coverage |
|---|---|---|---|---|---|
| SWE1-REQ-001 | Steering angle input ±720° | QT-001 | HIL Test | | ☐ |
| SWE1-REQ-002 | Assist torque output 0~12 Nm | QT-002 | HIL Test | | ☐ |
| SWE1-REQ-003 | Safety response < 10ms | QT-003 | HIL + Scope | | ☐ |
| SWE1-REQ-004 | DTC storage in NVM | QT-004 | HIL + Diag | | ☐ |
| SWE1-REQ-005 | CAN message cycle 20ms | QT-005 | CANoe Trace | | ☐ |
| SWE1-NFR-001 | Control loop ≤ 5ms | QT-006 | Oscilloscope | | ☐ |
| SWE1-NFR-002 | Boot time ≤ 200ms | QT-007 | Power cycle | | ☐ |
| | (모든 SWE.1 요구사항에 대해 기록) | | | | |

**Coverage Summary / 커버리지 요약:**
| Total Requirements | Tested | Not Tested | Coverage % |
|---|---|---|---|
| | | | |

---

## 4. System Test Scenarios / 시스템 시험 시나리오
<!-- GUIDE: 실제 차량 사용 시나리오를 기반으로 한 시스템 수준 시험 -->

| Scenario ID | Scenario / 시나리오 | Precondition | Steps | Expected | Result |
|---|---|---|---|---|---|
| QT-SC-001 | Normal driving: straight road at 60km/h | Engine running, speed=60 | 1.Steer ±10° slowly 2.Check assist | Smooth assist proportional to angle | |
| QT-SC-002 | Parking maneuver: low speed steering | Speed=0~5km/h | 1.Full lock left 2.Full lock right | Max assist torque, smooth response | |
| QT-SC-003 | Emergency steering at 100km/h | Highway speed | 1.Quick steer ±30° 2.Return to center | Fast response, stable assist | |
| QT-SC-004 | Sensor failure: steering angle | Normal driving | 1.Disconnect sensor 2.Check response | Safe state within 10ms, warning lamp ON | |
| QT-SC-005 | CAN communication loss | Normal driving | 1.Disconnect CAN bus 2.Wait 100ms | Timeout detected, degraded mode | |
| QT-SC-006 | Power cycle recovery | After fault | 1.Power off 2.Power on 3.Check state | Normal startup, DTC stored | |
| QT-SC-007 | Temperature extreme: cold start | -40°C soak | 1.Power on 2.Check all functions | All functions nominal within 200ms | |
| QT-SC-008 | Temperature extreme: hot operation | +85°C | 1.Full load operation 2.Check limits | Motor derating active, no shutdown | |

---

## 5. Non-Functional Test Results / 비기능 시험 결과

### 5.1 Performance / 성능

| Test | Requirement | Measured | Status |
|---|---|---|---|
| Control loop cycle time | ≤ 5 ms | | |
| CAN response time | ≤ 10 ms | | |
| Boot time | ≤ 200 ms | | |
| Interrupt latency | ≤ 50 μs | | |

### 5.2 Stress Test / 스트레스 시험

| Test | Duration | Condition | Result |
|---|---|---|---|
| Continuous operation | 72 hours | Full load, 25°C | |
| Rapid steering input | 1 hour | Max frequency ±720° | |
| CAN bus high load | 4 hours | 90% bus load | |

### 5.3 Resource Usage / 리소스 사용

| Resource | Budget | Measured | Margin | Status |
|---|---|---|---|---|
| RAM usage | ≤ 70% (44.8 KB) | | | |
| ROM usage | ≤ 80% (204.8 KB) | | | |
| CPU load (normal) | ≤ 60% | | | |
| CPU load (peak) | ≤ 70% | | | |

---

## 6. Regression Test Summary / 회귀 시험 요약

| Test Suite | Total | Passed | Failed | Blocked | Pass Rate |
|---|---|---|---|---|---|
| Functional Tests | | | | | |
| Safety Tests | | | | | |
| Performance Tests | | | | | |
| Communication Tests | | | | | |
| **Total** | | | | | |

---

## 7. Release Criteria Checklist / 릴리스 기준 체크리스트

| # | Criteria / 기준 | Target | Actual | Status |
|---|---|---|---|---|
| 1 | Requirements coverage | 100% | | ☐ |
| 2 | All qualification tests passed | 100% pass | | ☐ |
| 3 | No open critical/major defects | 0 | | ☐ |
| 4 | Code coverage (Statement) | ≥ 100% | | ☐ |
| 5 | Code coverage (Branch) | ≥ 100% | | ☐ |
| 6 | All SWE.1-6 documents Approved | 100% | | ☐ |
| 7 | V-Model traceability complete | 100% | | ☐ |
| 8 | Safety analysis complete (FMEA) | Done | | ☐ |
| 9 | Regression tests passed | 100% pass | | ☐ |
| 10 | MISRA-C violations resolved | 0 critical | | ☐ |

---

## 8. V-Model Traceability Summary / V-모델 추적성 요약

| V-Model Pair | Link Count | Coverage | Status |
|---|---|---|---|
| SWE.1 (Requirements) ↔ SWE.6 (Qualification Test) | | | |
| SWE.2 (Architecture) ↔ SWE.5 (Integration Test) | | | |
| SWE.3 (Detailed Design) ↔ SWE.4 (Unit Test) | | | |

---

## 9. Defect Summary / 결함 요약

| ID | Scenario | Severity | Description | Status |
|---|---|---|---|---|
| QT-DEF-001 | QT-SC-003 | (예시) Torque overshoot during quick steer | Closed |
| | | | | |

---

## 10. Conclusion & Recommendation / 결론 및 권고

### Assessment / 평가
- [ ] **PASS** - All release criteria met. SW ready for release.
- [ ] **CONDITIONAL PASS** - Minor issues remain. SW can be released with known limitations.
- [ ] **FAIL** - Critical issues found. SW NOT ready for release.

### Recommendations / 권고사항
1. (권고사항을 기록하세요)

---

## 11. Approval Block / 승인

| Role / 역할 | Name / 이름 | Signature / 서명 | Date / 날짜 |
|---|---|---|---|
| Test Engineer / 시험 담당자 | | | |
| Test Manager / 시험 관리자 | | | |
| Quality Assurance / 품질 보증 | | | |
| Project Manager / 프로젝트 관리자 | | | |

---

## 12. Review Criteria / 검토 기준
| # | Criteria | Check |
|---|---|---|
| 1 | All SWE.1 requirements have test cases (100% coverage) | ☐ |
| 2 | All test cases executed and results recorded | ☐ |
| 3 | System test scenarios cover normal + failure cases | ☐ |
| 4 | Non-functional tests completed | ☐ |
| 5 | Release criteria checklist evaluated | ☐ |
| 6 | V-Model traceability complete | ☐ |
| 7 | No open critical/major defects | ☐ |
| 8 | Approval signatures obtained | ☐ |

---
*Generated by ASPICE Process Manager*
